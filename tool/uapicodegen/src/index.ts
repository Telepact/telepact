const figlet = require("figlet");

console.log(figlet.textSync("uAPI - CodeGen"));

import * as fs from "fs";
import * as path from "path";
import * as Handlebars from "handlebars";
import { program } from "commander";

// Define command line arguments
program
  .option("-i, --input <path>", "input .uapi.json file")
  .option("-o, --output <path>", "output directory");

program.parse(process.argv);

const options = program.opts();

// Read the JSON file
const json = JSON.parse(fs.readFileSync(options.input, "utf8"));

// Compile the template
const template = Handlebars.compile(fs.readFileSync("template.hbs", "utf8"));

// Process each structure in the JSON file
for (const struct of json) {
  // Get the class name and properties from the structure
  const [className, properties] = Object.entries(struct)[0] as [
    string,
    Record<string, any>,
  ];

  // Prepare the data for the template
  const data = {
    className,
    properties: Object.keys(properties).map((key) => ({
      name: key,
      type: Array.isArray(properties[key])
        ? `List<${properties[key][0]}>`
        : typeof properties[key] === "object"
          ? `Map<String, ${properties[key][0]}>`
          : properties[key][0],
    })),
  };

  // Generate the Java code
  const javaCode = template(data);

  // Write the Java code to a file
  fs.writeFileSync(path.join(options.output, `${className}.java`), javaCode);
}
