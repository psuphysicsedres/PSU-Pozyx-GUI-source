#!/bin/bash
FILELIST="
graphing_realtime_2D.py
1D_ranging.py
3D_positioning.py
motion_data.py
configure_uwb_settings.py
"

distpath="PozyxGUI/pozyxgui/src/main/resources/scripts/unix"

for srcfile in ${FILELIST}
do
  pyinstaller --onefile --distpath ${distpath} -y ${srcfile}
done