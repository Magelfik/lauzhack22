/**
 * Initiates a discussion between the auth server. The discussion is incomplete
 * @param claims
 * @returns {Promise<any>}
 */
function init(claims){
    return fetch('http://localhost:8000/connection', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"claims": claims})
    }).then(response => response.json());
}

/**
 * Initiates the connection between the auth server and the client
 * @param token The connection token previously acquired by the init function (see below)
 * @param claims The required claims
 * @param on_success The on success callback. Will exclusively be called if all claims are present.
 * @param on_error The on error callback. Will be called otherwise.
 */
function init_websocket(token, claims, on_success, on_error){
    let ws = new WebSocket(`ws://localhost:8000/${token}/status`);

    ws.onmessage = function(event) {
        let payload = JSON.parse(event.data);
        
        if (claims.every(claim => payload.hasOwnProperty(claim))){
            on_success(payload);
        } else if (payload.hasOwnProperty('error')){
            on_error();
        }
    };
}

class AuthenticationStatus {
    constructor() {
        this.is_authed = false;
        this.is_denied = false;
        this.is_working = false;

        this.error = false;

        this.message = "";
    }
}