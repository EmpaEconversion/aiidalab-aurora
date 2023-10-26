from __future__ import annotations

import contextlib

import pandas as pd
from aiida.orm import Group, load_group
from aiida_aurora.schemas.battery import BatterySample, BatterySampleJsonTypes
from IPython.display import display as jupyter_display
from traitlets import HasTraits, Integer

from ..groups import SAMPLES_GROUP_PREFIX as GROUP_PREFIX
from .backends.backend import Backend
from .utils import get_valid, style, to_pd_query

Types: dict = BatterySampleJsonTypes

# TODO some operations are done on raw while others on samples - consolidate?


class SamplesModel(HasTraits):
    """A model used in Aurora to manage available samples.

    Available samples are loaded in from the associated backend
    and stored locally as a queryable `pandas` dataframe.

    Attributes
    ----------
    `updated` : `Integer`
        An observable samples update counter.
    `sample_ids` :` list[int]`
        A list of sample ids.
    `raw` : `list[dict]`
        The list of validated sample dictionaries.
    `models` : `list[BatterySample]`
        The list of validated sample models.
    `samples` : `pd.DataFrame`
        The local cache of available samples.
    """

    OPTIONS = {
        "Sample": "metadata.name",
        "Sub-batch": "metadata.subbatch",
        "Manufacturer": "specs.manufacturer",
        "Separator": "specs.composition.separator.name",
        "Cathode": "specs.composition.cathode.formula",
        "Anode": "specs.composition.anode.formula",
        "Electrolyte": "specs.composition.electrolyte.formula",
    }

    updated = Integer(0)

    def __init__(self, backend: Backend | None = None) -> None:
        """`SamplesModel` constructor.

        Parameters
        ----------
        `backend` : `Backend`
            The model's backend.
        """
        self.__backend = backend
        self.__raw: dict[int, dict] = {}
        self.__cache = pd.DataFrame()

        if self.__backend:
            self.__backend.init()

    @property
    def sample_ids(self) -> list[int]:
        """Return a list of sample ids.

        Returns
        -------
        `list[int]`
            A list of sample ids.
        """
        return list(self.__raw.keys())

    @property
    def raw(self) -> list[dict]:
        """Return a list of validated sample dictionaries.

        Returns
        -------
        `list[dict]`
            The list of validated sample dictionaries.
        """
        return list(self.__raw.values())

    @raw.setter
    def raw(self, samples: list[dict]) -> None:
        """Validate samples and store as dictionary.

        Parameters
        ----------
        `samples` : `list[dict]`
            The raw samples to be validated and stored.
        """
        self.__raw = {
            sample.id: sample.dict()
            for sample in get_valid(samples, schema=BatterySample)
        }

    @property
    def models(self) -> dict[int, BatterySample]:
        """Return the validated sample models.

        Returns
        -------
        `dict[int, BatterySample]`
            A list of validated sample models.
        """
        return {
            sample.id: sample
            for sample in get_valid(self.raw, schema=BatterySample)
        }

    @property
    def samples(self) -> pd.DataFrame:
        """Return samples as a flat dataframe.

        Serves as a queryable local cache of samples.

        Returns
        -------
        `pd.DataFrame`
            The samples dataframe cache.
        """
        if self.__raw and not self.has_samples():
            self.cache()
        return self.__cache.copy(deep=True)

    @samples.setter
    def samples(self, samples: pd.DataFrame) -> None:
        """Set samples to provided dataframe.

        Parameters
        ----------
        `samples` : `pd.DataFrame`
            A samples dataframe.
        """
        self.__cache = samples

    @property
    def highest_sample_id(self) -> int:
        """Return the highest sample id.

        Return 0 if samples dataframe is empty.

        Returns
        -------
        `int`
            The highest sample id.
        """
        return self.__cache.last_valid_index() if self.has_samples() else 0

    def set_backend(self, backend: Backend) -> None:
        """Set this model's backend.

        Parameters
        ----------
        `backend` : `Backend`
            The backend to associate with this model.
        """
        self.__backend = backend

    def has_batch(self, batch: str) -> bool:
        """Check if batch exists.

        Parameters
        ----------
        `batch` : `str`
            The batch id.

        Returns
        -------
        `bool`
            True if batch is present.
        """
        if self.has_samples():
            batches = self.__cache["metadata.batch"].drop_duplicates().values
            return batch in batches
        return False

    def has_samples(self) -> bool:
        """Check if any samples exist.

        Returns
        -------
        `bool`
            True if any samples exist.
        """
        return not self.__cache.empty

    def get_sample(self, sample_id: int) -> pd.DataFrame:
        """Return sample by id.

        Parameters
        ----------
        `sample_id` : `int`
            The sample id.

        Returns
        -------
        `pd.DataFrame`
            The `pd.DataFrame` sample row.
        """
        return self.query({"id": sample_id})

    def get_group_labels(self, discard="") -> list[str]:
        """Fetch group labels from cache.

        Returns
        -------
        `list[str]`
            A list of available group labels.
        """
        if self.has_samples():
            column = "metadata.groups"
            labels = list(self.__cache[column].explode().unique())
            # TODO simplify the following command
            labels.insert(0, labels.pop(labels.index("all-samples")))
            if discard:
                labels.remove(discard)
            return labels
        return []

    def get_group_samples(self, group: str) -> set[int]:
        """Return the samples set assigned to the given group.

        Parameters
        ----------
        `group` : `str`
            The group label.

        Returns
        -------
        `set[int]`
            The set of samples assigned to the given group.
        """
        column = "metadata.groups"
        condition = self.__cache[column].apply(lambda groups: group in groups)
        return set(self.__cache[condition].index)

    def save_group(self, ids: list[int], group: str) -> None:
        """Save group by attaching its label to selected samples.

        Discards group from all samples, then reattaches group only
        to selected samples.

        Parameters
        ----------
        `ids` : `list[int]`
            The selected sample ids.
        `group` : `str`
            The group label.
        """
        self.remove_from_group([], group)
        if ids:
            self.add_to_group(ids, group)
        self.updated += 1

    def add_to_group(self, ids: list[int], group: str) -> None:
        """Add selected samples to group.

        Parameters
        ----------
        `ids` : `list[int]`
            The selected sample ids.
        `group` : `str`
            The group label.
        """
        rows, column = ids or slice(None), "metadata.groups"
        self.__cache.loc[rows, column] = self.__cache.loc[rows, column].apply(
            lambda groups: groups | {group})

    def remove_from_group(self, ids: list[int], group: str) -> None:
        """Remove selected samples from group.

        Parameters
        ----------
        `ids` : `list[int]`
            The selected sample ids.
        `group` : `str`
            The group label.
        """
        rows, column = ids or slice(None), "metadata.groups"
        self.__cache.loc[rows, column] = self.__cache.loc[rows, column].apply(
            lambda groups: groups - {group})

    def get_aiida_groups(self) -> list[Group]:
        """docstring"""
        return Group.collection.find({
            "label": {
                "like": f"{GROUP_PREFIX}/%",
            },
        })

    def update_aiida_groups(self, groups: dict[str, set[int]]) -> None:
        """docstring"""
        for label, ids in groups.items():
            self.remove_from_aiida_group(ids, label)
        self.discard_empty_aiida_groups(groups)

    def remove_from_aiida_group(self, ids, label):
        """docstring"""
        with contextlib.suppress(Exception):
            group = load_group(f"{GROUP_PREFIX}/{label}")
            group.remove_nodes(nodes=[
                sample for sample in group.nodes if sample.id not in ids
            ])

    def discard_empty_aiida_groups(self, groups):
        """docstring"""
        for group in self.get_aiida_groups():
            label = group.label.removeprefix(f"{GROUP_PREFIX}/")
            if label not in groups and label != "all-samples":
                Group.collection.delete(group.pk)

    def assign_subbatch(self, ids: list[int], subbatch: str) -> None:
        """Assign a sub-batch label to the given samples.

        Parameters
        ----------
        `ids` : `list[int]`
            The samples to update.
        `subbatch` : `str`
            The sub-batch label.
        """
        self.__cache.loc[ids, "metadata.subbatch"] = subbatch
        self.updated += 1

    def load(self) -> None:
        """Fetch and store new schema-modeled validated samples."""
        if self.__backend is not None:
            self.raw = self.__backend.fetch()
            self.cache()

    def save(self) -> None:
        """Persist the current valid samples in the backend."""
        if self.__backend is not None:
            self.__backend.save(self.raw)

    def cache(self) -> None:
        """Process raw samples as `pd.DataFrame`.

        The dataframe is first normalized (flattned), then typed
        according to the corresponding `aiida_aurora.schemas` schema.

        Datetime fields are converted to `datetime` for future
        serialization.

        Caching also increments the `new_data_trigger` observable.
        """

        df = pd.json_normalize(self.raw)

        if not df.empty:
            df = df.astype({c: t for c, t in Types.items() if c in df})
            df.set_index("id", drop=True, inplace=True)
            key = "metadata.creation_datetime"
            df[key] = pd.to_datetime(df[key])

        self.__cache = df
        self.updated += 1

    def update(self, sample: BatterySample, cache=True, save=True) -> None:
        """Update sample.

        Optionally cache and/or persist.

        Parameters
        ----------
        `sample` : `BatterySample`
            The updated sample.
        `cache` : `Optional[bool]`
            If the samples are to be cached after operation.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        self.__raw[sample.id] = sample.dict()
        if cache:
            self.cache()
        if save:
            self.save()

    def add(self, sample: BatterySample, cache=True, save=True) -> None:
        """Add sample.

        Optionally cache and/or persist.

        Parameters
        ----------
        `sample` : `BatterySample`
            The new sample.
        `cache` : `Optional[bool]`
            If the samples are to be cached after operation.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        if sample.id in self.__raw:
            raise KeyError(f"sample {sample.id} already exists.")
        self.update(sample, cache, save)

    def add_many(
        self,
        samples: list[BatterySample],
        cache=True,
        save=True,
    ) -> None:
        """Add multiple samples.

        Optionally cache and/or persist.

        Parameters
        ----------
        `samples` : `list[BatterySample]`
            A list of new samples.
        `cache` : `Optional[bool]`
            If the samples are to be cached after operation.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        for sample in samples:
            self.add(sample, cache=False, save=False)
        if cache:
            self.cache()
        if save:
            self.save()

    def delete(self, sample_id: int, cache=True, save=True) -> None:
        """Delete sample.

        Optionally cache and/or persist.

        Parameters
        ----------
        `sample_id` : `int`
            The id of the sample to be deleted.
        `cache` : `Optional[bool]`
            If the samples are to be cached after operation.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        if sample_id not in self.__raw:
            raise KeyError(f"sample {sample_id} does not exist.")
        del self.__raw[sample_id]
        if cache:
            self.cache()
        if save:
            self.save()

    def delete_many(
        self,
        sample_ids: list[int],
        cache=True,
        save=True,
    ) -> None:
        """Delete multiple samples.

        Optionally cache and/or persist.

        Parameters
        ----------
        `sample_ids` : `list[int]`
            The list of sample ids to be deleted.
        `cache` : `Optional[bool]`
            If the samples are to be cached after operation.
        `save` : `Optional[bool]`
            If the samples are to be persisted after operation.
        """
        for sid in sample_ids:
            self.delete(sid, cache=False, save=False)
        if cache:
            self.cache()
        if save:
            self.save()

    def copy(self, include_backend=False) -> SamplesModel:
        """Return a copy of this model.

        Optionally include this model's backend.

        Parameters
        ----------
        `include_backend` : `bool`
            Attache this model's backend to copy if True,
            `False` by default.

        Returns
        -------
        `SamplesModel`
            A copy of this model.
        """
        copy = SamplesModel()
        copy.sync(self)
        if include_backend and self.__backend:
            copy.set_backend(self.__backend)
        return copy

    def sync(self, other: SamplesModel) -> None:
        """Synchronize this model with another.

        Parameters
        ----------
        `other` : `SamplesModel`
            Another instance of this class against which to sync.
        """
        self.raw = other.raw
        self.cache()

    def query(
        self,
        query: dict,
        project: str | list[str] | None = None,
    ) -> pd.DataFrame:
        """Fetch available samples.

        Optionally filter samples by a set of conditions and/or
        return specific columns if requested.

        Parameters
        ----------
        `query` : `dict`
            A dictionary of query conditions.
        `project` : `Optional[Union[str, list[str]]]`
            A column or list of columns to return, `None` by default.
            If `None`, return all columns.

        Returns
        -------
        `pd.DataFrame`
            A dataframe of available samples, optionally filtered.
        """

        if not self.has_samples():
            return self.__cache

        df = self.samples
        if group := query.pop("group", None):
            field = "metadata.groups"
            df = df[df[field].apply(lambda groups: group in groups)]

        pd_query = to_pd_query(query) or "id"
        results = df.query(pd_query)

        if not project or results.empty:
            return results

        return self._project_results(results, project)

    def display(self, df: pd.DataFrame) -> None:
        """Display a styled samples dataframe.

        Parameters
        ----------
        `df` : `pd.DataFrame`
            The samples dataframe to be displayed.
        """
        if not df.empty:
            jupyter_display(style(df))

    def get_options_legend(self) -> str:
        """Return a `|`-separated specs legend.

        Returns
        -------
        `str`
            The specs legend string.
        """
        return " | ".join(self.OPTIONS)

    def as_options(self, df: pd.DataFrame) -> list[tuple[str, int]]:
        """Parse dataframe as `(label, index)` select options.

        Parameters
        ----------
        `df` : `pd.DataFrame`
            A samples dataframe.

        Returns
        -------
        `list[tuple[str, int]]`
            A list of `(label, index)` select options.
        """
        # TODO figure out how to attach a legend as a disabled first option
        # TODO this is an open issue in ipywidgets
        # options = [(" ".join(f" {label:12s}" for label in self.OPTIONS), -1)]
        options: list[tuple[str, int]] = []
        options.extend((self.as_option(row), i) for i, row in df.iterrows())
        return options

    def as_option(self, row: pd.Series) -> str:
        """Parse `pandas.Series` row as option string for sample
        selection list.

        Parameters
        ----------
        `row` : `pd.Series`
            A battery sample info row.

        Returns
        -------
        `str`
            A processed string representation of the sample info. Used
            to display sample options in sample selection list.
        """
        return " ".join(f" {row[val]:12s}" for val in self.OPTIONS.values())

    def _project_results(
        self,
        results: pd.DataFrame,
        project: str | list[str],
    ) -> pd.DataFrame:
        """Project results onto requested fields.

        Parameters
        ----------
        `results` : `pd.DataFrame`
            A samples dataframe.
        `project` : `str | list[str]`
            A field or fields on which to project the dataframe.

        Returns
        -------
        `pd.DataFrame`
            The projected dataframe.
        """

        if not isinstance(project, list):
            project = [project]

        return results[project]

    def __contains__(self, id: int) -> bool:
        return id in self.__raw

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SamplesModel):
            return NotImplemented
        return self.samples.equals(other.samples)
