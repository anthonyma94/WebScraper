const getProfile = {
  async: true,
  crossDomain: true,
  url: "/api/profile",
  method: "GET",
  data: {},
  success: function (response) {
    hardCodeForm(response);
  },
  error: function (response) {
    alert(`error updating from api\n ${response}`);
  },
};

const postProfile = {
  url: "/api/profile",
  method: "POST",
  data: {},
  dataType: "json",
  headers: {
    "Content-Type": "application/json",
  },
  success: function (response) {
    $.ajax(getProducts);
    console.log("success");
  },
  error: function (response) {
    alert(`Error sending from api ${response}`);
  },
};

function updateProfile(response) {
  $("email").val(response["email"]);
  updateForm(response["shipping_address"]);
  updateForm(response["credit_card"]);
}
function updateForm(response, form) {
  $.each(response, function (i, product) {
    $("#tableBody").append(`
        
    `);
  });
}

function hardCodeForm(response) {
  // console.log(response);
  $("#billing_address #email").val(response[0]["email"]);
  $("#shipping_address #email").val(response[0]["email"]);
  let sp = response[0]["shipping_address"];
  let cc = response[0]["credit_card"];
  let ba = cc["billing_address"];
  console.log(`check check ${ba["first_name"]}`);
  $.each(sp, function (key, val) {
    $(`#shipping_address #${key}`).val(val);
  });

  $.each(cc, function (key, val) {
    $(`#credit_card #${key}`).val(val);
  });

  $.each(ba, function (key, val) {
    $(`#billing_address #${key}`).val(val);
  });
}

$("#saveBtn").click(function (e) {
  e.preventDefault();

  $(this).data("previous", $(this).html());
  $(this).html(`
      <span class='spinner-border spinner-border-sm' role='status'></span>
      <span>Adding...</span>
      `);
  let request = postProfile;
  let data;
  data = {
    id: 1,
    email: $("#email").val(),
    shipping_address: build_data("#shipping_address"),
    credit_card: build_data("#credit_card"),
  };
  console.log(data);
  data["credit_card"]["billing_address"] = build_data("#billing_address");
  request["data"] = data;
  console.log(request["data"]);
  $.post(request).done(() => $(this).html($(this).data("previous")));
});

function build_data(formID) {
  let info = {};
  formData = $(`${formID} .form-control`);

  $.each(formData, function (key, val) {
    if (val.id == "email") {
    } else {
      info[val.id] = val.value;
    }
  });
  info["id"] = 1;
  return info;
}

$.ajax(getProfile);
