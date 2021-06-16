const postProfile = {
    url: "/api/profile",
    method: "POST",
    data: {},
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (response) {
        $.ajax(getProfile);
        console.log("success");
    },
    error: function (response) {
        console.error(response);
        alert(`Error sending from api ${response.responseText}`);
    },
};

const validator = {
    // debug: true,
    ignore: ".ignore",
    rules: {
        email: "email",
        card_number: "creditcard",
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
        let id = $(form).data("id");

        sa = build_data([
            ...$(form).find(
                `#shipping_address-${id} input, #shipping_address-${id} select`
            ),
        ]);

        ba = $("#same-shipping").is(":checked")
            ? { ...sa }
            : build_data([
                  ...$(
                      `#billing_address-${id} input, #billing_address-${id} select`
                  ),
              ]);

        cc = build_data([
            ...$(`#credit_card-${id} input, #credit_card-${id} select`),
        ]);
        cc.billing_address = ba;

        profile = {
            id: id,
            email: $(`#email-${id}`).val(),
            shipping_address: sa,
            credit_card: cc,
        };

        request.data = JSON.stringify(profile);

        $.ajax(request);
    },
};

function build_data(form) {
    data = {};

    form.forEach((item) => {
        data = { ...data, [item.name]: item.value };
    });

    return data;
}

$(document).ready(function () {
    $(document).on("click", ".editButton", function (e) {
        e.preventDefault();
        let id = $(this).data("id");
        $(`#collapse-${id} input, #collapse-${id} select`).prop(
            "disabled",
            false
        );
        $(`.saveButton[data-id=${id}]`).removeClass("d-none").show();

        $(`#form-${id}`)
            .validate(validator)
            .submit(function (e) {
                e.preventDefault();
            });
    });
});
