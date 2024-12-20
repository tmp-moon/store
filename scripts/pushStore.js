const fs = require("fs").promises;
const yaml = require("js-yaml");
const path = require("path");
const fetch = require("node-fetch");

const STORE_URL = process.env.STORE_URL || "https://api.beamlit.dev/v0";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
const IMAGE = process.env.IMAGE;

const parseYaml = async (type, func) => {
  const yamlPath = path.join(type, func, "beamlit.yaml");
  const yamlContent = await fs.readFile(yamlPath, "utf8");
  const parsedYaml = yaml.load(yamlContent);
  return parsedYaml;
};

const pushStore = async (type, func) => {
  const content = await parseYaml(type, func);
  content.image = IMAGE;
  const response = await fetch(
    `${STORE_URL}/admin/store/${type}/${content.name}`,
    {
      method: "PUT",
      body: JSON.stringify(content),
      headers: {
        Authorization: `Basic ${Buffer.from(
          ADMIN_USERNAME + ":" + ADMIN_PASSWORD
        ).toString("base64")}`,
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 seconds
    }
  );
  if (response.status !== 200) {
    throw new Error(
      `Failed to push ${type} ${func} to store, cause ${await response.text()}`
    );
  }
};

module.exports = pushStore;
