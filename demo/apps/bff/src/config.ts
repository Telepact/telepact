import path from "node:path";
import { fileURLToPath } from "node:url";

export interface DemoConfig {
  demoRoot: string;
  port: number;
  browserSchemaDir: string;
  staticDir: string;
  todoServiceUrl: string;
  plannerServiceUrl: string;
}

export function resolveDemoRoot(): string {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../");
}

export function loadConfig(): DemoConfig {
  const demoRoot = resolveDemoRoot();
  return {
    demoRoot,
    port: Number.parseInt(process.env.PORT ?? "3000", 10),
    browserSchemaDir: process.env.BROWSER_SCHEMA_DIR ?? path.join(demoRoot, "schemas", "browser"),
    staticDir: process.env.STATIC_DIR ?? path.join(demoRoot, "apps", "bff", "static"),
    todoServiceUrl: process.env.TODO_SERVICE_URL ?? "http://127.0.0.1:7001/api",
    plannerServiceUrl: process.env.PLANNER_SERVICE_URL ?? "http://127.0.0.1:7002/api",
  };
}
