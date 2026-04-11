// No Telepact library required

const request = [
  {},
  {
    "fn.divide": {
      x: 10,
      y: 2,
    },
  },
];

const response = await fetch("/api/telepact", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(request),
});

const [headers, body] = await response.json();

if (body.Ok_) {
  console.log(body.Ok_.result);
} else {
  console.error(headers, body);
}
