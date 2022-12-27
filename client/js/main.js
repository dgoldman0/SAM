// Source code uses examples from https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications
status = 'connecting';

$(document).ready(function() {
  const urlParams = new URLSearchParams(window.location.search);
  // Yes I know this isn't a secure way to do things, but for now it's fine and I'm too exhausted to create a better system.
  username = urlParams.get('username');
  password = urlParams.get('password');
  if ("WebSocket" in window) {
    var ws = new WebSocket("ws://localhost:9381");
    const f = document.getElementById("chat-history");

    ws.onopen = function() {
      // Web Socket is connected. You can send data by send() method.
      f.innerHTML = "Connecting..."
    };

    ws.onmessage = async function(event) {
      msg = await event.data.text();
      console.log(msg)
      switch (status) {
        case 'connecting':
        if (msg == "SAM Chat Interface") {
          await ws.send(new Blob(["AUTH:" + username]));
          status = "salt"
        } else {
        }
        break;
        case 'salt':
        if (msg.startsWith("CHALLENGE:$2b")) {
          // The 2a replacement is due to salt version. See https://github.com/ircmaxell/password_compat/issues/49
          salt = "$2y" + msg.substring(13);
          hashed_pw = dcodeIO.bcrypt.hashSync(password, salt);
          hashed_pw = "$2b" + hashed_pw.slice(3);
          console.log(hashed_pw)
          await ws.send(new Blob([hashed_pw]));
          status = "verifying";
        }
        break;
        case 'verifying':
          if (msg == "WELCOME") {
            f.innerHTML = "Connection Established."
            status = "connected";
            $("#chat-form").submit(async function(e) {
              e.preventDefault();
              input = $("#msg");
              msg = input.val();
              input.val("")
              await ws.send(new Blob([msg]));
              f.innerHTML += `<br/>&lt;${username}&gt;: ${msg}`;
              input.focus();
              return false;
            });
          }
        break;
        default:
          f.innerHTML += `<br/>&lt;SAM&gt;: ${msg}`;
      }
    };

    ws.onclose = function(event) {
      if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
      } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        console.log('[close] Connection died');
      }
    };
  } else {
    // the browser doesn't support WebSocket.
    alert("Websockets not supported.")
  }
});