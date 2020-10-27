const getProducts = {
  async: true,
  crossDomain: true,
  url: "http://localhost:5000/api/products?=",
  method: "GET",
  data: {},
  success: function (response) {
    updateTable(response);
  },
  error: function (response) {
    alert(`error updating from api\n ${response}`);
  },
};

const postProducts = {
  url: "http://localhost:5000/api/products?=",
  method: "POST",
  data: { url: "" },
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

function updateTable(response) {
  console.log(response);
  $.each(response, function (i, product) {
    $("#tableBody").empty();
    $("#tableBody").append(`
        <tr>
            <td scope="row">
                ${product["id"]}
            </td>
            <td>
                ${product["name"]}
            </td>
            <td>
                NA
            </td>
            <td>
                <a href='${product["url"]}'>BestBuy.ca</a>
            </td>
            <td>
            False
            </td>
        </tr>
    `);
  });
}

$("#addBtn").click(function (e) {
  e.preventDefault();
  url = $("#url").val();
  if (url == "") {
    alert("No value for URL");
    return false;
  } else {
    request = postProducts;
    request["data"] = `{"url": "${url}"}`;
    console.log(request);
    $.post(request);
  }
});

$.ajax(getProducts);
