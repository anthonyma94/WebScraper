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
  contentType: "application/json; charset=utf-8",
  dataType: "json",
  success: function (response) {
    console.log("success");
  },
  error: function (response) {
    console.error(response);
    alert(`Error sending from api ${response.responseText}`);
  },
};

function hardCodeForm(response) {
  $("input[name=id]").first().val(response[0]["id"]);
  $("#email").val(response[0]["email"]);
  let sp = response[0]["shipping_address"];
  let cc = response[0]["credit_card"];
  let ba = cc["billing_address"];
  $.each(sp, function (key, val) {
    $(`#shipping_address *[name=${key}]`).val(val);
  });

  $.each(cc, function (key, val) {
    $(`#credit_card *[name=${key}]`).val(val);
  });

  $.each(ba, function (key, val) {
    $(`#billing_address *[name=${key}]`).val(val);
  });
}

$.validator.addMethod(
  "postalCode",
  function (value) {
    return /^[a-zA-Z][0-9][a-zA-Z][0-9][a-zA-Z][0-9]$/.test(value);
  },
  "Please enter a valid postal code."
);

$("form").validate({
  // debug: true,
  ignore: ".ignore",
  rules: {
    email: "email",
    // card_number: "creditcard",
    phone_number: "phoneUS",
    postal_code: "postalCode",
  },
  submitHandler: function (form) {
    //   $(this).data("previous", $(this).html());
    //   $(this).html(`
    // <span class='spinner-border spinner-border-sm' role='status'></span>
    // <span>Adding...</span>
    // `);
    let request = postProfile;

    sa = build_data([
      ...$("#shipping_address input, #shipping_address select"),
    ]);

    ba = $("#same-shipping").is(":checked")
      ? { ...sa }
      : build_data([...$("#billing_address input, #billing_address select")]);

    cc = build_data([...$("#credit_card input, #credit_card select")]);
    cc.billing_address = ba;

    ac = build_data([...$("#account_info input")]);

    profile = {
      email: $("#email").val(),
      account: ac,
      shipping_address: sa,
      credit_card: cc,
    };

    if (
      $("input[name=id]").first().val() !== undefined &&
      $("input[name=id]").first().val() !== ""
    ) {
      profile = { id: $("#id").val(), ...profile };
    }

    request.data = JSON.stringify(profile);

    console.log(request);

    $.ajax(request).then(() => (window.locaion.href = "/profiles"));
  },
});

function build_data(form) {
  data = {};

  form.forEach((item) => {
    data = { ...data, [item.name]: item.value };
  });

  return data;
}

function handleSameBilling() {
  if ($("#same-shipping").is(":checked")) {
    $("#billing_address").addClass("d-none").hide();
    $("#billing_address input, #billing_address select").addClass("ignore");
  } else {
    $("#billing_address").removeClass("d-none").show();
    $("#billing_address input, #billing_address select").removeClass("ignore");
  }
}

handleSameBilling();

$("#same-shipping").change(handleSameBilling);
