echo 'Setting up processing enviroment'
echo 'Fetching Photogrammetry data from scanner'
python3 fetch.py
echo 'Starting Reduced detail processing photogrammetry operation, will take ~1.5 minutes'
rm outputscan.usdz
/Applications/images/operation /Applications/images /Applications/images/outputscan.usdz -d reduced
echo 'Remove waste products'
rm processing*.png