@echo off

pyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win graphing_realtime_2D.py -y

pyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win 1D_ranging.py -y

pyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win 3D_positioning.py -y

pyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win motion_data.py -y

pyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win configure_uwb_settings.py -ypyinstaller --distpath PozyxGUI/pozyxgui/src/main/resources/scripts/win console_printing.py -y