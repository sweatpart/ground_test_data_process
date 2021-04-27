function askServer() {
    var date = document.getElementById("date").value;
    var req = new XMLHttpRequest();
    req.open("POST", "/update/" + date, true);
    req.onreadystatechange = handleServerResponse;
    req.send();
    document.getElementById("return").innerHTML = "The request has been sent.";
}

function handleServerResponse() {
    if ((this.readyState == 4) && (this.status == 200)) {
        var result = this.responseText;
        document.getElementById("return").innerHTML = result;
    }
}