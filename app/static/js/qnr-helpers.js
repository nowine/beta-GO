'user strict';
var QNRLoader = (function() {
  var _answers;
  var _questionKey;
  var _next;
  var _questionNote;
  var _button;
  var _current; //Current Question

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
    if (type_code === 'RADIO') {
      var $ol = $("<ol>", { "class": "list-group", "type": "A"});
      $dd.append($ol);
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
        $ol.append($li);
      }
    } else if (type_code === 'NUMERIC' || type_code === 'TEXT') {
      if ('label' in question.labels) {
        // If there is a label provided, add it to <dd> before the input field,
        // and then remove it from the obj. The rest object attributes can be
        // used to create <input> field.
        $dd.val(question.labels['label']);
        question.labels['label'] = undefined;
      }
      var $input = $("<input>", {
        type: "text",
        name: question.key
      });
      $input.attr(question.labels); // quetions.labels should contain other attributes for the input.
      $dd.append($input);
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
    if (!_current.type_code || _current.type_code === "RADIO") {
      var $selected = _questionNote.find('li input:radio:checked');
      if ($selected.val()===null) {
        alert("请先选择一个选项，然后继续。");
        return false;
      }
      _answers[_questionKey] = $selected.val();
    } else {
      var $input = $("input[type=text]");
      var inputValue = $input.val();
      if (inputValue === null) {
        alert("请输入答案，然后继续");
        return false;
      }
      if (_current.type_code === "NUMERIC") {
        inputValue = parseInt(inputValue, 10);
        if (isNaN(inputValue)) {
          alert("该问题仅接受纯数字答案，请重新输入。");
          return false;
        }
      }
      _answers[_questionKey] = inputValue;
    }
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
      _current = json.question.detail;
      _questionKey = json.question.detail.key;
      _next = json.question.next_seq;
      _questionNote.empty();
      _questionNote.append(formatQuestion(_current));
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
