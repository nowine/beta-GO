var QNRLoader2 = (function() {
  var _answers;
  var _questionKey;
  var _next;
  var _questionNote;
  var _button;

  function formatQuestion(question) {
    var type_code;
    if (question.type_code) {
      type_code = question.type_code;
    } else {
      type_code = 'RADIO';
    } //by default set the type_code as 'RADIO'
    var $div = $("<div>", { id: question.key, class: type_code });
    var $dt = $("<dt>", {
      html: question.body
    });
    $div.append($dt);
    var $dd = $("<dd>");
    $div.append($dd);
    var $list, inputType;
    if (type_code == 'RADIO') {
      $list = $("<ol>", { "class": "list-group", "type": "A"});
      inputType = 'radio';
    } else if (type_code == 'NUMERIC' || type_code == 'TEXT') {
      $list = $("<ul>", {"class": "list-group"});
      inputType = 'text';
    }
    $dd.append($list);
    var $li, $input;
    for (prop in question.labels) {
      $li = $("<li>");
      $input = $("<input>", {
        type: "radio",
        name: question.key,
        value: prop
      });
      $li.append($input);
      $li.append(question.labels[prop]);
      $list.append($li);
    }
    return $div;
  }

  function init($question, $button) {
    _answers = {}; //blank object
    _next = 1;
    _questionNote = $question;
    _button = $button;
  }

  function addAnswer() {
    var $selected = _questionNote.find('li input:radio:checked');
    if ($selected.val()==null) {
      alert("请先选择一个选项，然后继续。");
      return false;
    }
    _answers[_questionKey] = $selected.val();
    return true;
  }

  function isLast() {
    return _next < 1;
  }

  function getQuestion(url) {
    var ajaxSetting = {
      url: url,
      data: {
        sequence: _next,
        answers: _answers
      },
      type: 'GET',
      dataType: 'json',
    }
    $.ajax(ajaxSetting).done(function (json) {
      var question = json.question.detail;
      _questionKey = json.question.detail.key;
      _next = json.question.next_seq;
      _questionNote.empty();
      _questionNote.append(formatQuestion(question));
      if (_next > 0) {
        _button.val('继续');
      } else {
        _button.val('提交');
      }
    }).fail(function (data) {
      alert("failed");
    });
  }

  function makeApprasal(url) {
    var ajaxSetting = {
      url: url,
      data: JSON.stringify({ answers: _answers }),
      contentType: "application/json",
      type: "POST",
    }
    $.ajax(ajaxSetting).done(function (data) {
      _questionNote.empty();
      _button.val("返回");
      alert('Success');
    });
  }

  return {
    init: init,
    getQuestion: getQuestion,
    addAnswer: addAnswer,
    isLast: isLast,
    makeApprasal: makeApprasal
  };

})();
