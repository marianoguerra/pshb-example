var ui = {};
ui.user = "";

ui.init = function () {
    ui.app.run();
    $("#send-message").click(ui.onSendMessageClick);
    $("#login-button").click(ui.onLoginClick);
    ui.app.setLocation("#/");
};

ui.crossFade = function (toHide, toShow, onFinish) {
    $(toHide).fadeOut(function () {
            setTimeout(function () {
                $(toShow).fadeIn(onFinish)
            }, 500);
    });
};

ui.error = function (msg) {
    console.error(msg);
};

ui.errorCb = function (msg) {
    return function () {
        ui.error(msg);
    };
};

ui.loadStream = function (path, offset, limit) {
    offset = offset || 0;
    limit = limit || 20;

    req.get(path + offset + "/" + limit + "/", ui.onLoadStreamOk, ui.errorCb("couldn't load stream"));
};

ui.onLoadStreamOk = function (msgs) {
    var i;

    $("#stream").html("");

    for (i = msgs.length - 1; i >= 0; i -= 1) {
        ui.prependMessage(msgs[i]);
    }
};

ui.onLoginClick = function () {
    if (ui.user != "") {
        ui.error("already logged in");
        return;
    }

    var user = $("#user").val().trim(),
        password = $("#password").val().trim();

    if (user == "") {
        ui.error("empty user");
        return;
    }

    if (password == "") {
        ui.error("empty password");
        return;
    }

    req.post("/a/login/", {"user": user, "password": password}, ui.onLoginOk, ui.onLoginError);
};

ui.onLoginOk = function (response) {
    if (response.ok) {
        $("#user").val("");
        $("#password").val("");

        ui.user = response.user;
        ui.crossFade("#login", "#form", function () { $("#message").focus(); });
        ui.crossFade("#login-btn", "#logout-btn");
        $("#signup-btn").fadeOut();
        ui.app.setLocation("#/timeline/" + ui.user);
        ;
    }
    else {
        ui.onLoginError();
    }
};

ui.onLoginError = function () {
    ui.error("login failed");
    $("#password").val("");
};

ui.logout = function () {
    ui.user = "";
    ui.crossFade("#form", "#login");
    ui.crossFade("#logout-btn", "#login-btn");
    $("#signup-btn").fadeIn();
    ui.app.setLocation("#/");
};

ui.goMain = function () {
    ui.loadStream("/a/messages/");
};

ui.onSendMessageClick = function () {
    var text = $("#message").val().trim(),
        user = ui.user;

    if (text == "") {
        ui.error("empty message");
        return;
    }

    if (user == "") {
        ui.error("empty user");
        return;
    }

    req.create("/a/message/", model.message(text, user), ui.onSendMessageOk, ui.errorCb("couldn't save message"));

    return false;
};

ui.onSendMessageOk = function (msg) {
    ui.prependMessage(msg);
    $("#message").val("");
};

ui.prependMessage = function (msg) {
    $("#msg-tpl").tmpl(msg).prependTo("#stream");
};

ui.showTagInStream = function (context) {
    ui.loadStream("/a/messages/tag/" + this.params.tag + "/");
};

ui.showUserStream = function (context) {
    ui.loadStream("/a/messages/from/" + this.params.user + "/");
};

ui.showUserTimelineStream = function (context) {
    ui.loadStream("/a/timeline/" + this.params.user + "/");
};

ui.showLogin = function (context) {
    ui.crossFade("#form", "#login", function () { $("#user").focus(); });
};

ui.app = $.sammy(function() {
    this.get('#/', ui.goMain);
    this.get('#/tag/:tag', ui.showTagInStream);
    this.get('#/login', ui.showLogin);
    this.get('#/logout', ui.logout);
    this.get('#/user/:user', ui.showUserStream);
    this.get('#/timeline/:user', ui.showUserTimelineStream);
});

