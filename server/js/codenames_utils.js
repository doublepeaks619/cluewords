jQuery.each( [ "put", "delete", "post", "get" ], function( i, method ) {
    jQuery[ method ] = function( url, data, callback, type ) {
        if ( jQuery.isFunction( data ) ) {
        type = type || callback;
        callback = data;
        data = undefined;
        }

        return jQuery.ajax({
        url: url,
        type: method,
        processData: false,
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        success: callback
        });
    };
});

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};