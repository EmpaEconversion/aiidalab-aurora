# AiiDAlab Aurora installation on Windows PC

## 1. Basic software

- Install Python 3, if you do not have it yet\
  https://realpython.com/installing-python/#how-to-install-python-on-windows

- Install Miniconda\
  https://docs.conda.io/en/latest/miniconda.html

- Install pip\
  https://www.geeksforgeeks.org/how-to-install-pip-on-windows/?ref=lbp

- Install the Windows Subsystem for Linux (WSL2)\
  https://learn.microsoft.com/en-us/windows/wsl/install \
  In principle this is not mandatory, Docker can also use Hyper-V (a Windows feature that must be enabled).

  Make sure WSL is version 2. This may require an update (you will get a message if needed).

- Install the Ubuntu distribution e.g.

  ```
  wsl --install -d Ubuntu
  ```

- Install Docker
  https://docs.docker.com/desktop/install/windows-install/

- Launch it, and from settings -> Resources -> WSL integration -> enable WSL2 Ubuntu

## 2. AiiDAlab

- Open a terminal and install `aiidalab-launch`

  ```
  pip install aiidalab-launch
  ```

  User manual: https://aiidalab.readthedocs.io/en/latest/usage/index.html#aiidalab-launch

- Change the default docker image (Note: Docker should be running)

  ```
  aiidalab-launch profiles edit default
  ```

  and modify the file into this:

  ```
  port = 8888
  default_apps = [ "aiidalab-widgets-base",]
  system_user = "aiida"
  image = "aiidalab/aiidalab-docker-stack:22.8.1"
  home_mount = "aiidalab_default_home"
  extra_mount = []
  ```

- If you get an error saying it cannot connect to Docker, it might be due to a Windows bug. Run this:

  ```
  python <path-to-python-end>\Scripts\pywin32_postinstall.py -install
  ```

  where `<path-to-python-end>` might be `C:\Users\USERNAME\Miniconda3` and `USERNAME` it is your Windows terminal username.

- From the terminal run:

  ```
  aiidalab-launch start
  ```

- If it works well, you will get an URL like `https://localhost:8888/...`\
  Open it in a browser.

- If you get an error, it might be due to a bug of `aiidalab-launch`. No worries. Run this

  ```
  docker ps -a
  ```

  and find the ID of the container and check if it is up and running.\
  Then run

  ```
  docker exec -it CONTAINERID /bin/bash
  ```

  where `CONTAINERID` is the ID that you just found. This will connect to a shell within the Docker container. Then:

  ```
  su aiida
  jupyter notebook list
  ```

  You will get a long URL, with a token (`token=...`).

  Go to https://localhost:8888 and enter token and a new password. Remember this password, it may be asked to you in the future if you restart the container.

  AiiDAlab should finally open! :-)

## 3. AiiDA configuration

- Open a Terminal within AiiDAlab (or run `docker exec -it CONTAINERID /bin/bash` in a shell).
  Everything that follow is executed in this terminal, unless otherwise stated.
  You must make sure you are login as `aiida` user, by doing:

  ```
  su aiida
  ```

- Set up SSH passwordless login to the LAB pc:

  ```
  ssh-keygen
  cd
  cat ~/.ssh/id_rsa.pub
  ```

  Copy the key that was just printed (contained in the `~/.ssh/id_rsa.pub` file) to the LAB pc into this file (create it if it is not there):

  ```
  C:\Users\USERNAME\.ssh\authorized_keys
  ```

  or if you are an admin:

  ```
  C:\ProgramData\ssh\administrator_authorized_keys
  ```

  (a way to edit this file might be to open a PowerShell as administrator (right click-administrator) and run `Notepad C:\ProgramData\ssh\administrator_authorized_keys`).

- install all the git repos of the plugins:

  ```
  pip install dgbowl-schemas

  mkdir ~/src

  cd ~/src
  git clone https://github.com/lorisercole/aiida-core.git
  cd aiida-core
  git checkout windows
  pip install -e .

  cd ~/src
  git clone https://github.com/ramirezfranciscof/aiida-calcmonitor.git
  cd aiida-calcmonitor
  git checkout tom_mon_bug_fixes
  pip install -e .

  cd ~/src
  git clone https://github.com/epfl-theos/aiida-aurora.git
  cd aiida-aurora
  pip install -e .

  cd
  mkdir ~/aiida_run
  reentry scan
  verdi daemon restart --reset
  ```

  NOTE: in some computers python still uses the `aiida-core` installed in the root directory, so you will get an error about the transport (`shell_type`). To fix this, log into the Docker container and install `aiida-core` by hand:

  ```
  docker exec -it CONTAINERID /bin/bash
  # the user will be root
  cd /home/aiida/src/aiida-core
  pip install .
  ```

  Then restart the daemon from an AiiDAlab Terminal.

- If everything went well

  ```
  verdi plugin list aiida.schedulers
  ```

  should list the tomato scheduler;

  ```
  verdi plugin list aiida.calculations
  ```

  should list the aurora and calcmonitor calculations plugins.

- Now, for example from the AiiDAlab Explorer, navigate to `aiida-aurora/examples/config_files`
  and modify the files to match your installation:

  - the `username` and `key_filename` in `computer_ddm07162_config.yml`
  - the `remote_abs_path` in `code_ketchup-0.2rc2.yml`. This will probably be
    ```
    remote_abs_path: "/Users/USERNAME/Miniconda3/envs/tomato/Scripts/ketchup.exe"
    ```
    Find where the `ketchup.exe` code is located in the LAB pc. NOTE that here we write the path without `C:` and using `/` instead of `\`.

- ***In the LAB pc***, open the file (create the folder and file, if they are not present)

  ```
  C:\Users\USERNAME\Documents\WindowsPowerShell\profile.ps1
  ```

  and add this line

  ```
  Set-Alias -Name ketchup -value C:\Users\svfe\Miniconda3\envs\tomato-0.2rc2\Scripts\ketchup.exe
  ```

  (where you insert the correct path to `ketchup.exe`).\
  This will allow one to call ketchup without loading the virtual environment (which is essential for the AiiDA scheduler).
  You can check that this works from the LAB pc, by opening a new terminal and entering `ketchup --version`. If it runs, it works!

- Back to the AiiDAlab terminal, let's run

  ```
  cd ~/src/aiida-aurora/examples/config_files
  ./setup.sh
  ```

  This should configure all the computers and codes needed by Aurora.

- You can test the connection to the LAB computer and localhost with

  ```
  verdi computer test ddm07162
  verdi computer test localhost-verdi
  ```

  (NOTE: the first test will return one error about `echo`. This is normal).

- Create the necessary AiiDA groups:

  ```
  verdi create group BatterySamples
  verdi create group CyclingSpecs
  verdi create group CalcJobs
  verdi create group MonitorJobs
  ```

## 4. Aurora app installation

- Setup custom app store (if Aurora not available in the official app store)
  https://aiidalab.readthedocs.io/en/latest/admin/index.html

  ```
  # apps.yaml
  aurora:
  releases:
    - url: 'git+https://github.com/epfl-theos/aiidalab-aurora@develop'
      metadata:
        categories:
        - utilities
        logo: https://raw.githubusercontent.com/aiidalab/aiidalab-widgets-base/master/miscellaneous/logos/aiidalab.png
        title: Aurora BIG-MAP app
        description: An AiiDAlab application for the Aurora BIG-MAP Stakeholder initiative.
        authors: Loris Ercole
        external_url: https://github.com/epfl-theos/aiidalab-aurora
        documentation_url: https://github.com/epfl-theos/aiidalab-aurora#readme
  ```

- Install Aurora app
  If the version is not correct, or it does not update. You can update by hand in this way:

  ```
  cd ~/apps/aurora
  git checkout develop
  git pull
  ```

  Then reload AiiDAlab page.

- The Tasks button shows all the open windows/notebooks/terminals. Shut them down if you do not use them anymore.

- To update the list of available samples, edit the JSON file `~/apps/aurora/available_samples.json`.
