var httpGet = function(url, username, password, callback) {
    return jQuery.ajax({
        url: url,
        type: 'get',
        beforeSend: function ajaxBeforeSend(jqXHR) {
            jqXHR.withCredentials = true;
            jqXHR.setRequestHeader("Authorization", "Basic " + btoa(encodeURIComponent(escape(username)) + ":" + encodeURIComponent(escape(password))));
        },
        success: callback,
        error: function(jqXHR, textStatus, errorThrown) {
            alert(jqXHR.status + '\n' + textStatus + '\n' + errorThrown);
        }
    });
};

var httpDelete = function(url, username, password, callback) {
    return jQuery.ajax({
        url: url,
        type: 'delete',
        beforeSend: function ajaxBeforeSend(jqXHR) {
            jqXHR.withCredentials = true;
            jqXHR.setRequestHeader("Authorization", "Basic " + btoa(encodeURIComponent(escape(username)) + ":" + encodeURIComponent(escape(password))));
        },
        success: callback,
        error: function(jqXHR, textStatus, errorThrown) {
            alert(jqXHR.status + '\n' + textStatus + '\n' + errorThrown);            
        }
    });
};

var httpPost = function(url, data, username, password, callback) {
    return jQuery.ajax({
        url: url,
        type: 'post',
        processData: false,
        beforeSend: function ajaxBeforeSend(jqXHR) {
            jqXHR.withCredentials = true;
            jqXHR.setRequestHeader("Authorization", "Basic " + btoa(encodeURIComponent(escape(username)) + ":" + encodeURIComponent(escape(password))));
        },
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        success: callback,
        error: function(jqXHR, textStatus, errorThrown) {
            alert(jqXHR.status + '\n' + textStatus + '\n' + errorThrown);            
        }
    });
};

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