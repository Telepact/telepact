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

// Validate required CLI arguments
if (!options.input || !options.output) {
    console.error("Error: Both --input and --output options are required.");
    process.exit(1);
}

// Read the JSON file
const json = JSON.parse(fs.readFileSync(options.input, "utf8"));

// Compile the template
const template = Handlebars.compile(
    fs.readFileSync("dist/templates/javatemplate.hbs", "utf8"),
);

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
            type: properties[key],
        })),
    };

    console.log(`data: ${JSON.stringify(data)}`);

    // Generate the Java code
    const javaCode = template(data);

    console.log("Generating code.");

    // Check if the directory exists
    if (!fs.existsSync(options.output)) {
        // Create the directory if it doesn't exist
        fs.mkdirSync(options.output, { recursive: true });
    }

    // Write the Java code to a file
    fs.writeFileSync(path.join(options.output, `${className}.java`), javaCode);
}
