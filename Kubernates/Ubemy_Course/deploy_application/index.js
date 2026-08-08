const express = require("express");
const app = express();
const port = process.env.PORT || 3000;
const env_val = process.env.APP_NAME || "TestMSG"

app.get("/", (req, res) => {
  res.send(`Hello World from a dockerized app! ${env_val} `);
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
