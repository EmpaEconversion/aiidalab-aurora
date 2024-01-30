.. _development:

Development Guide
#################

.. note::

   If you have yet to do so, we recommend you first check out the :ref:`tutorial <tutorial>` to learn the basics of using the app.

Aurora is open-source and as such, welcomes community contribution. To contribute to the development of the Aurora ecosystem, we recommend following these steps:

#. Fork the plugin and app repositories

   * plugin: ``https://github.com/epfl-theos/aiida-aurora.git``
   * app: ``https://github.com/epfl-theos/aiidalab-aurora.git``

   .. important::

      Requires a GitHub account.

#. Install the app **locally** (see :ref:`installation guide <installation>`)

   a. Follow the local Docker-based installation guide of AiiDAlab
   b. Open AiiDAlab in the browser
   c. Open the AiiDAlab terminal and run the following code:

      .. code::

         mkdir ~/src

         cd ~/src
         git clone https://github.com/<your-github-username>/aiida-aurora.git
         cd aiida-aurora
         pip install -e .[testing,docs]

         cd ~/apps
         git clone https://github.com/<your-github-username>/aiidalab-aurora.git aurora
         cd aurora
         pip install -e .[docs]

         mkdir ~/aiida_run

#. Install *tomato* **locally** - run ``pip install tomato`` from the AiiDAlab terminal
#. Open a separate terminal and run ``tomato -vv`` to start the *tomato* server
#. From the main terminal, run ``ketchup status`` to verify that the server is up
#. Set up AiiDA by running the following from terminal: (see :ref:`aiida setup <aiida_setup>` for more information)

   .. code::

      verdi computer setup \
      --description "localhost running the tomato scheduler"
      --label "localhost"
      --hostname "localhost"
      --transport "core.local"
      --scheduler "tomato"
      --work_dir "/home/jovyan/aiida_run/"
      --mpirun_command "mpirun -np {tot_num_mpiprocs}"
      --mpiprocs_per_machine 1
      --shebang "#!/bin/bash"
      --prepend_text ""
      --append_text ""

      verdi computer configure core.local \
      --safe_interval: 0.0
      --use_login_shell: true

      verdi code create \
      --label "ketchup-local"
      --computer "localhost"
      --description "ketchup submit"
      --input_plugin "aurora.cycler"
      --on_computer true
      --remote_abs_path "/opt/conda/bin/ketchup"
      --use_double_quotes False
      --prepend_text ""
      --append_text ""

----

Once you finish applying, committing, and pushing your changes, please create a PR to the `epfl-theos` accounts and await review.
