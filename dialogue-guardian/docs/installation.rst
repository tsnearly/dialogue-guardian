Installation
============

Requirements
------------

* Python 3.7 or higher
* FFmpeg installed and accessible in your system's PATH

Installing FFmpeg
-----------------

**macOS (using Homebrew):**

.. code-block:: bash

   brew install ffmpeg

**Ubuntu/Debian:**

.. code-block:: bash

   sudo apt update
   sudo apt install ffmpeg

**Windows:**

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the files and add the ``bin`` directory to your system PATH
3. Verify installation by running ``ffmpeg -version`` in Command Prompt

Installing Dialogue Guardian
----------------------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install dialogue-guardian

From Source
~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/yourusername/dialogue-guardian.git
   cd dialogue-guardian
   pip install -e .

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~

For development work:

.. code-block:: bash

   git clone https://github.com/yourusername/dialogue-guardian.git
   cd dialogue-guardian
   pip install -e .
   pip install -r dev-requirements.txt

Verification
------------

Verify the installation by running:

.. code-block:: bash

   guardian --version

You should see the version number displayed.