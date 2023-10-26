from datetime import datetime
from pathlib import Path
from typing import List

import ipywidgets as ipw
import pandas as pd
from aiida_aurora.schemas.battery import BatterySample
from ipyfilechooser import FileChooser

from aurora.common.models.samples import SamplesModel
from aurora.time import TZ


class SamplesImporter(ipw.Accordion):
    """
    docstring
    """

    def __init__(self, model: SamplesModel) -> None:
        """docstring"""

        self.model = model

        self.filepath_explorer = FileChooser(
            Path.home(),
            layout={
                "margin": "5px",
            },
        )

        self.description = ipw.Text(
            layout={
                "width": "auto",
            },
            description="Description:",
            placeholder="Description for the battery",
            value="Li-based",
            disabled=True,
        )

        self.batch = ipw.Text(
            layout={
                "flex": "1",
                "margin": "2px 10px 2px 2px",
            },
            description="Batch:",
            placeholder="Full name `<batch>-##`",
            value=datetime.now(TZ).date().strftime(r"%y%m%d"),
            disabled=True,
        )

        self.manufacturer = ipw.Text(
            layout={},
            style={
                "description_width": "initial",
            },
            description="Manufacturer:",
            placeholder="Name of the manufacturer",
            value="Empa",
            disabled=True,
        )

        self.process = ipw.Text(
            layout={
                "flex": "1",
                "margin": "2px 10px 2px 2px",
            },
            description="C. process:",
            placeholder="Creation process",
            value="Created by robot",
            disabled=True,
        )

        self.cdate_picker = ipw.DatePicker(
            layout={},
            description="C. date:",
            value=datetime.now(TZ).date(),
            disabled=True,
        )

        self.import_button = ipw.Button(
            layout={
                "height": "92px",
                "margin": "auto"
            },
            button_style="primary",
            description="Import Samples",
            tooltip="Import samples",
            disabled=True,
            icon="fa-upload",
        )

        self.import_warning = ipw.HTML()

        super().__init__(
            layout={},
            children=[
                ipw.VBox(
                    layout={
                        "align_items": "stretch",
                    },
                    children=[
                        self.filepath_explorer,
                        ipw.HBox(
                            layout={},
                            children=[
                                ipw.VBox(
                                    layout={
                                        "flex": "1",
                                        "margin": "0 20px 0 0",
                                    },
                                    children=[
                                        self.description,
                                        ipw.HBox(
                                            layout={
                                                "justify_content":
                                                "space-between"
                                            },
                                            children=[
                                                self.batch,
                                                self.manufacturer,
                                            ],
                                        ),
                                        ipw.HBox(
                                            layout={
                                                "justify_content":
                                                "space-between"
                                            },
                                            children=[
                                                self.process,
                                                self.cdate_picker,
                                            ],
                                        ),
                                    ],
                                ),
                                self.import_button,
                            ],
                        ),
                        self.import_warning,
                    ],
                ),
            ],
            selected_index=None,
        )

        self.set_title(0, "Import samples from robot output")

        self._set_event_listeners()

    def reset(self, _=None) -> None:
        """docstring"""
        self.filepath_explorer.reset()
        self.on_filepath_select()

    def on_filepath_select(self, _=None) -> None:
        """docstring"""
        self.batch.disabled = self.filepath_explorer.selected is None
        self.description.disabled = self.filepath_explorer.selected is None
        self.manufacturer.disabled = self.filepath_explorer.selected is None
        self.process.disabled = self.filepath_explorer.selected is None
        self.cdate_picker.disabled = self.filepath_explorer.selected is None
        self.check_if_importable()

    def check_if_importable(self, _=None) -> None:
        """docstring"""
        self.import_warning.value = ""
        disabled = False
        disabled = disabled or self.filepath_explorer.selected is None
        disabled = disabled or self.batch.value == ""
        disabled = disabled or self.description.value == ""
        disabled = disabled or self.manufacturer.value == ""
        disabled = disabled or self.process.value == ""
        self.import_button.disabled = disabled

    def import_samples(self, _=None) -> None:
        """Import samples from selected path."""

        if (filepath := self.filepath_explorer.selected) is None:
            return

        batch = self.batch.value

        if self.model.has_batch(batch):
            warning = "<span style='color: red'><strong><em>"
            warning += f"Batch {batch} already exists"
            warning += "</em></strong></span>"
            self.import_warning.value = warning
            return

        base = {
            "batch": self.batch.value,
            "manufacturer": self.manufacturer.value,
            "description": self.description.value,
            "creation_date": self.cdate_picker.value,
            "creation_process": self.process.value,
        }

        uploaded_samples = self._parse_robot_output(filepath, base)
        self.model.add_many(uploaded_samples, save=False)

    def _parse_robot_output(
        self,
        filepath: str,
        base: dict,
    ) -> List[BatterySample]:
        """docstring"""

        try:

            with open(filepath) as robot_output:
                df = pd.read_csv(robot_output, sep=";")

            highest_id = self.model.highest_sample_id
            df["id"] = df["Battery_Number"] + highest_id

            samples = []
            for i, row in df.iterrows():
                sample = self._parse_sample(base, row)
                samples.append(sample)
                if i == 0:
                    base["battery_capacity"] = sample.specs.capacity.nominal

            return samples

        except Exception:
            return []

    def _parse_sample(self, base: dict, df: pd.Series) -> BatterySample:
        """docstring"""

        anode_W = df["Anode Weight"] / 1000
        cathode_W = df["Cathode Weight (mg)"] / 1000
        anode_cc_W = df["Anode Current Collector Weight (mg)"] / 1000
        cathode_cc_W = df["Cathode Current Collector Weight (mg)"] / 1000
        anode_net_W = anode_W - anode_cc_W
        cathode_net_W = cathode_W - cathode_cc_W
        anode_practical_C = df["Anode Practical Capacity (mAh/g)"]
        cathode_practical_C = df["Cathode Practical Capacity (mAh/g)"]
        anode_C = anode_net_W * anode_practical_C
        cathode_C = cathode_net_W * cathode_practical_C
        C = base.get("battery_capacity", round(min(anode_C, cathode_C), 3))

        date = base["creation_date"]

        time = datetime.now(TZ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ).time()

        creation_datetime = datetime.combine(date, time)

        initdict = {
            "id": df["id"],
            "specs": {
                "manufacturer": base["manufacturer"],
                "case": df["Casing Type"],
                "composition": {
                    "description": base["description"],
                    "anode": {
                        "formula": df["Anode Type"],
                        "position": df["Anode Position"],
                        "diameter": {
                            "nominal": df["Anode Diameter"],
                        },
                        "weight": {
                            "total": anode_W,
                            "collector": anode_cc_W,
                            "net": anode_net_W,
                            "units": "g",
                        },
                        "capacity": {
                            "nominal": anode_practical_C,
                        },
                    },
                    "cathode": {
                        "formula": df["Cathode Type"],
                        "position": df["Cathode Position"],
                        "diameter": {
                            "nominal": df["Cathode Diameter (mm)"],
                        },
                        "weight": {
                            "total": cathode_W,
                            "collector": cathode_cc_W,
                            "net": cathode_net_W,
                            "units": "g",
                        },
                        "capacity": {
                            "nominal": cathode_practical_C,
                        },
                    },
                    "electrolyte": {
                        "formula": df["Electrolyte"],
                        "position": df["Electrolyte Position"],
                        "amount": df["Electrolyte Amount"],
                    },
                    "separator": {
                        "name": df["Separator"],
                        "diameter": {
                            "nominal": df["Separator Diameter (mm)"],
                        },
                    },
                    "spacer": {
                        "value": df["Spacer (mm)"],
                    }
                },
                "capacity": {
                    "nominal": C,
                    "units": "mAh",
                },
            },
            "metadata": {
                "name": base["batch"] + "-" + str(df["Battery_Number"]),
                "batch": base["batch"],
                "creation_datetime": creation_datetime,
                "creation_process": base["creation_process"]
            }
        }

        return BatterySample(**initdict)

    def _set_event_listeners(self) -> None:
        """docstring"""
        self.filepath_explorer.register_callback(self.on_filepath_select)
        self.import_button.on_click(self.import_samples)
        self.batch.observe(self.check_if_importable, "value")
        self.description.observe(self.check_if_importable, "value")
        self.manufacturer.observe(self.check_if_importable, "value")
        self.process.observe(self.check_if_importable, "value")
