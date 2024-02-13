def get_infomap_script(lat, lon):

    # No "<script>" or "</script>" is needed for dynamic loading
    return """
        // Define latitude, longitude and zoom level
        const latitude = %.6f;
        const longitude = %.6f;
        const zoom = 12;

        // Set DIV element to embed map
        var mymap = L.map('infomap');

        // Add initial marker & popup window
        var mmr = L.marker([0,0]);
        mmr.bindPopup('0,0');
        mmr.addTo(mymap);

        // Add copyright attribution
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {
            foo: 'bar',
            attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}
        ).addTo(mymap);

        // Set lat lng position and zoom level of map
        mmr.setLatLng(L.latLng(latitude, longitude));
        mymap.setView([latitude, longitude], zoom);

        // Set popup window content
        mmr.setPopupContent('Latitude: '+latitude+' <br /> Longitude: '+longitude).openPopup();

        // Set marker onclick event
        mmr.on('click', openPopupWindow);

        // Marker click event handler
        function openPopupWindow(e) {
            mmr.setPopupContent('Latitude: '+e.latlng.lat+' <br /> Longitude: '+e.latlng.lng).openPopup();
        }
        """ % (lat , lon)
