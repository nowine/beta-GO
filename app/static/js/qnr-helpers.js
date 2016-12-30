'user strict';
var QNRLoader = (function() {
  var _answers;
  var _questionKey;
  var _next;
  var _questionNote;
  var _button;
  var _current; //Current Question
  var BMI = "BMI";
  var MBP = "最高血压1";
  var MBP2 = "最高血压2";
  var RADIO = "RADIO";
  var NUMERIC = "NUMERIC";
  var TEXT = "TEXT";

  function formatRadioQuest($div, question) {
    var $dt = $("<dt>", {
      html: question.body
    });
    $div.append($dt);
    var $dd = $("<dd>");
    $div.append($dd);
    var $ol = $("<ol>", {
      "class": "list-group",
      "type": "A"
    });
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
    return $div;
  }

  function formatTextQuest($div, question) {
    var $dt = $("<dt>", {
      html: question.body
    });
    $div.append($dt);
    var $dd = $("<dd>");
    $div.append($dd);
    if ("label" in question.labels) {
      $dd.val(question.labels["label"]);
      question.labels["label"] = undefined;
    }
    var $input = $("<input>", {
      type: "text",
      name: question.key
    });
    $input.attr(question.labels); // quetions.labels should contain other attributes for the input.
    $dd.append($input);
    return $div;
  }

  function formatNumberQuest($div, question) {
    return formatTextQuest($div, question);
  }

  function formatQuestion(question) {
    var $div = $("<div>", { id: "Anchor" });
    var $sub_div;
    do {
        $sub_div = $("<div>", { id: question.key, class: question.type_code });
        // Special Handling BMI question
        if (question.key === BMI) {
          $div.append(formatBMI($sub_div, question));
          break;
        }
        // For normal questions, formats based on type_code
        if (question.type_code === RADIO) {
          $sub_div = formatRadioQuest($sub_div, question);
        } else if (question.type_code === NUMERIC) {
          $sub_div = formatNumberQuest($sub_div, question);
        } else {
          // type_code === "TEXT"
          $sub_div = formatTextQuest($sub_div, question);
        }
        $div.append($sub_div);
        question = question.linked_to;
    } while (question != undefined);
    return $div;
  }

  function formatBMI($div, question) {
    var $dt = $("<dt>", {
      html: question.body
    });
    $div.append($dt);
    var $dd = $("<dd>");
    $div.append($dd);

    var $table = $('<table>', {border: "0"});
    $dd.append($table);
    // Format 2 rows for height and weight
    var $tr = $('<tr>');
    var $td = $('<td>', {html: "身高："});
    $tr.append($td);
    var $input = $('<input>', {id: "BMIheight"});
    $tr.append($('<td>').append($input));
    $table.append($tr);
    $tr = $('<tr>');
    $td = $('<td>', {html: "体重："});
    $tr.append($td);
    $input = $('<input>', {id: "BMIweight"});
    $tr.append($('<td>').append($input));
    $table.append($tr);

    return $div;
  }

  function init($question, $button) {
    _answers = {}; //blank object
    _next = 1;
    _questionNote = $question;
    _button = $button;
  }

  function validateAnswer() {
    var $anchor = $("#Anchor");
    var $divs = $anchor.find('div');
    var $sub_div, $input, i, inputValue;
    for (i=0; i<$divs.length; i++) {
      $sub_div = $divs.eq(i);
      if ($sub_div[0].id === "BMI") {
        return validateBMIAnswer();
      }
      if ($sub_div.hasClass(RADIO)) {
        $input = $sub_div.find('li input:radio:checked');
        if ($input.val()===null || $input.val()===undefined) {
          showError("请选择一个选项，然后继续。");
          return false;
        }
        _answers[$sub_div.id] = $input.val();
      } else {
        $input = $sub_div.find("input[type=text]");
        inputValue = $input.val();
        if (inputValue===null || inputValue===undefined || inputValue==="") {
          showError("请输入答案，然后继续。");
          return false;
        }
        if ($sub_div.hasClass(NUMERIC)) {
          inputValue = parseInt(inputValue);
          if (isNaN($input.val())) {
            showError("请输入数字。");
            return false;
          }
        }
        _answers[$sub_div[0].id] = inputValue;
      }
    }
    return true;
  }

  function __validateAnswer() {
    if (_questionKey != "BMI" && _questionKey != MBP && _questionKey != MBP2) {
      if (_current.type_code || _current.type_code === RADIO) {
        var $selected = _questionNote.find('li input:radio:checked');
        if ($selected.val()===null || $selected.val()===undefined) {
          showError("请先选择一个选项，然后继续。");
          return false;
        }
      } else {
        var $input = $("input[type=text]");
        var inputValue = $input.val();
        if (inputValue === null || inputValue === undefined) {
          showError("请输入答案，然后继续。");
          return false;
        }
        if (_current.type_code === NUMERIC) {
          inputValue = parseInt(inputValue, 10);
          if (isNaN(inputValue)) {
            showError("该问题答案仅支持数字，请重新输入。");
            return false;
          }
        }
      }
      return true;
    } else if (_questionKey === BMI){
      return validateBMIAnswer();
    }
  }

  function validateBMIAnswer(){
    //TODO: waiting for implementation
    var height = $("#BMIheight").val();
    if (height === "" || height === undefined || height === null) {
      showError("请输入身高。");
      return false;
    }
    var weight = $("#BMIweight").val();
    if (weight === "" || weight === undefined || weight === null) {
      showError("请输入体重。");
      return false;
    }
    if (isNaN(height) || isNaN(weight)) {
      showError("该问题答案仅支持数字，请重新输入。");
      return false;
    }
    height = parseInt(height, 10);
    weight = parseInt(weight, 10);
    var weight = weight/100;
    var bmi = height / weight / weight;
    _answers[BMI] = bmi;
    return true;
  }

  function showError(errorMsg) {
    //TODO to be enhanced for more fasion error message displaying
    alert(errorMsg);
  }

  function addAnswer() {
    if (_questionKey === BMI) {
      addBMIAnswer();
      return;
    }
    if (!_current.type_code || _current.type_code === RADIO) {
      var $selected = _questionNote.find('li input:radio:checked');
      _answers[_questionKey] = $selected.val();
    } else {
      var $input = $("input[type=text]");
      var inputValue = $input.val();
      inputValue = parseInt(inputValue, 10);
      _answers[_questionKey] = inputValue;
    }
  }

  function addBMIAnswer() {
    var height = parseInt($("#BMIheight").val());
    var weight = parseInt($("#BMIweight").val())/100;
    var bmi = height / weight / weight;
    _answers[_questionKey] = bmi;
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
    validateAnswer: validateAnswer,
//    addAnswer: addAnswer,
    isLast: isLast,
    makeApprasal: makeApprasal
  };

})();
