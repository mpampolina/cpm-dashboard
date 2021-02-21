const express = require("express");
const { spawn } = require("child_process");

const router = express.Router();

const computeCPM = (keyword, raw_activities) => {
  return new Promise((resolve, reject) => {
    const process = spawn("python", [".\\routes\\api\\api.py", keyword]);
    let output_data = "";

    process.stdout.on("data", (data) => {
      /* concatenate console data to output_data */
      output_data += data.toString();
    });

    process.stdin.write(JSON.stringify(raw_activities));
    process.stdin.end();

    /* print errors to console */
    process.stderr.on("data", (data) => {
      console.log("stderr: " + data);
      reject("Oops. Something went wrong.");
    });

    process.on("close", (code) => {
      console.log(`Python child process closing all stdio with code: ${code}`);
      /* return data as a JavaScript Object */
      resolve(JSON.parse(output_data));
    });
  });
};

router.post("/prob-critical", (req, res) => {
  computeCPM("PCritical", req.body)
    .then((data) => {
      res.json(data);
    })
    .catch((err) => {
      console.log(err);
      res.status(400).json({ msg: "Something went wrong." });
    });
});

router.post("/cdf", (req, res) => {
  computeCPM("CDF", req.body)
    .then((data) => {
      res.json(data);
    })
    .catch((err) => {
      console.log(err);
      res.status(400).json({ msg: "Something went wrong." });
    });
});

router.post("/activities", (req, res) => {
  computeCPM("Activities", req.body)
    .then((data) => {
      res.json(data);
    })
    .catch((err) => {
      console.log(err);
      res.status(400).json({ msg: "Something went wrong." });
    });
});

module.exports = router;
