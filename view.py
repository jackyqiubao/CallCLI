def viewhtml(uuid, filename='sparse.glb'):
    html = f'''
    <!DOCTYPE html>
    <html>
        <head>
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.2.0/model-viewer.min.js"></script>
        </head>
        <body>
            <model-viewer src="/{uuid}/{filename}" ar ar-modes="webxr scene-viewer quick-look" camera-controls tone-mapping="aces" poster="poster.webp" shadow-intensity="1.11" shadow-softness="0.82" camera-orbit="15.18deg 78.64deg 1.159m" field-of-view="30deg">
                <div class="progress-bar hide" slot="progress-bar">
                    <div class="update-bar"></div>
                </div>
            </model-viewer>
        </body>
    </html>
    '''
    return html