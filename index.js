const express = require("express");

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use("/api", require("./routes/api/cpm"))

app.listen(PORT, () => {
  console.log(`Server started on port: ${PORT}`);
});
