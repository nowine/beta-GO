var QNRLoader = (function(){
  var _questions = [];
  var _qnrKey;

  function formatQuestion(question) {
    var $div = $("<div>", { id: question.key });
    var $dt = $("<dt>", {
      html: question.body
    });
    $div.append($dt);
    var $dd = $("<dd>");
    $div.append($dd);
    var $ul = $("<ul>", { "class": "list-group" });
    $dd.append($ul);
    var $li, $input;
    for (prop in question.answers) {
      $li = $("<li>");
      $input = $("<input>", {
        type: "radio",
        name: question.key,
        value: prop
      });
      $li.append($input);
      $li.append(question.answers[prop]);
      $ul.append($li);
    }
    return $div;
  }

  function initialLoading(path, qnrKey) {
    _qnrKey = qnrKey;
    var ajaxSetting = {
      url: path,
      type: 'GET',
      async: false,
      dataType: 'json'
    };
    var jqxhr = $.ajax(path, ajaxSetting).done(function (data) {
      _questions = data.Questions;
      var length = _questions.length;
      var qn = $('#question');
      // Formatting Questions
      for (i=0; i<length; i++) {
        qn.append(formatQuestion(_questions[i].Question));
      }
      alert(length);
    }).fail(function (data) {
      alert("failed");
    }).always(function (data) {
      alert("Call Completed");
    });
  }
  return {
    initialLoading: initialLoading
  };
})();
