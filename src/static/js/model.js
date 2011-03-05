var model = {};

model.message = function (text, user, created) {
    return {"text": text || "", "user": user || null, "created": created || (new Date()).getTime()};
};
