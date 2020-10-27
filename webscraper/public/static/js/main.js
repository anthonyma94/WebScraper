const getProducts = {
  async: true,
  crossDomain: true,
  url: "http://localhost:5000/api/products?=",
  method: "GET",
  headers: {
    "content-type": "application/json",
    authorization:
      "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDEyNTY5MDgsIm5iZiI6MTYwMTI1NjkwOCwianRpIjoiNGM0MTcyMWItZjE1Mi00YWZjLWFkYmItOTZkOWM5YjY2NDQxIiwiZXhwIjoxNjAxODYxNzA4LCJpZGVudGl0eSI6ImFkbWluIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIiwidXNlcl9jbGFpbXMiOlsiYWRtaW4iXX0.NkuvpCv-ZP-H4DiO2VIBBnNG-abDc3Pgbhlj94Vng58",
  },
  processData: false,
  data: { username: "admin", password: "Password1" },
};

const postProducts = {
  async: true,
  crossDomain: true,
  url: "http://localhost:5000/api/products?=",
  method: "POST",
  headers: {
    "content-type": "application/json",
    authorization:
      "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDEyNTY5MDgsIm5iZiI6MTYwMTI1NjkwOCwianRpIjoiNGM0MTcyMWItZjE1Mi00YWZjLWFkYmItOTZkOWM5YjY2NDQxIiwiZXhwIjoxNjAxODYxNzA4LCJpZGVudGl0eSI6ImFkbWluIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIiwidXNlcl9jbGFpbXMiOlsiYWRtaW4iXX0.NkuvpCv-ZP-H4DiO2VIBBnNG-abDc3Pgbhlj94Vng58",
  },
  processData: false,
  data: { username: "admin", password: "Password1", url: "" },
};

$.ajax(getProducts).done(function (response) {
  $.each(response, function (i, product) {
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
});
