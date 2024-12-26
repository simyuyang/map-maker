from flask import Flask, render_template, request, redirect, send_file
import pygmt
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def mapper():
    if request.method == 'POST':
        try:
            lonmin = float(request.form['lonmin'])
            lonmax = float(request.form['lonmax'])
            latmin = float(request.form['latmin'])
            latmax = float(request.form['latmax'])

            pygmt.config(MAP_FRAME_TYPE='plain', FORMAT_GEO_MAP='ddd.xx')
            fig = pygmt.Figure()
            fig.basemap(
                region=[lonmin,lonmax,latmin,latmax],
                projection="M20c",
                frame='af'
            )
            fig.coast(
                shorelines=True,
                land='black',
                water='skyblue'
            )

            if request.form.get('seismicity'):
                seismicity = pd.read_csv('data/isc-gem-cat.csv', skiprows=109, sep=r'\s*,\s*', engine='python')
                seismicity_filtered = seismicity[(seismicity['lat'] > latmin) & (seismicity['lat'] < latmax) & (seismicity['lon'] > lonmin) & (seismicity['lon'] < lonmax) & (seismicity['mw'] > 4)]
                pygmt.config(COLOR_BACKGROUND='red', COLOR_FOREGROUND='white')
                pygmt.makecpt(cmap='buda', series=[0, 100], reverse=True, overrule_bg=True)
                fig.plot(
                    x=seismicity_filtered['lon'],
                    y=seismicity_filtered['lat'],
                    style='cc',
                    fill=seismicity_filtered['depth'],
                    cmap=True,
                    size=0.002 * 2 ** seismicity_filtered['mw'],
                    pen='0.5p,black'
                )
                fig.colorbar(
                    cmap=True,
                    frame='xaf+lDepth of seismic events (km)',
                    position='JBL+jBL+o0.5c/2c+w6h+e',
                    box='+gwhite+p1p'
                )

            fig.savefig('static/maps/map.png')

            return redirect('/')
        except ValueError:
            return 'Please input valid coordinates for latitude and longitude'
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)