import express from "express";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  Message,
  Server,
  ServerOptions,
  TelepactSchema,
  TelepactSchemaFiles,
} from "telepact";
import { DemoConfig, loadConfig } from "./config.js";
import { createTelepactRequester } from "./telepactHttp.js";

function createSchema(schemaDir: string): TelepactSchema {
  const files = new TelepactSchemaFiles(schemaDir, fs, path);
  return TelepactSchema.fromFileJsonMap(files.filenamesToJson);
}

export function createApp(config: DemoConfig = loadConfig()): express.Express {
  const schema = createSchema(config.browserSchemaDir);
  const todoService = createTelepactRequester(config.todoServiceUrl);
  const plannerService = createTelepactRequester(config.plannerServiceUrl);

  const handler = async (requestMessage: Message): Promise<Message> => {
    const functionName = requestMessage.getBodyTarget();
    const normalize = (message: Message) => new Message(message.headers ?? {}, message.body);
    const normalizeTodoMutation = (body: Record<string, unknown>) => {
      const [target, payload] = Object.entries(body)[0] ?? [];
      if (!target || typeof payload !== "object" || payload === null) {
        return body;
      }
      return {
        [target]: {
          ...payload,
          dueDate: (payload as Record<string, unknown>).dueDate ?? "",
        },
      };
    };

    if (functionName === "fn.getHomeData") {
      const [todosResponse, dashboardResponse] = await Promise.all([
        todoService.request({
          "fn.listTodos": {
            status: "all",
            search: "",
            project: "",
            tag: "",
          },
        }),
        plannerService.request({ "fn.getPlannerDashboard": {} }),
      ]);

      if (todosResponse.getBodyTarget() !== "Ok_") {
        return normalize(todosResponse);
      }
      if (dashboardResponse.getBodyTarget() !== "Ok_") {
        return normalize(dashboardResponse);
      }

      return new Message({}, {
        Ok_: {
          home: {
            todos: todosResponse.getBodyPayload().todos,
            dashboard: dashboardResponse.getBodyPayload().dashboard,
          },
        },
      });
    }

    if (
      functionName === "fn.listTodos" ||
      functionName === "fn.toggleTodoCompletion" ||
      functionName === "fn.deleteTodo"
    ) {
      return normalize(await todoService.request(requestMessage.body, requestMessage.headers));
    }

    if (functionName === "fn.createTodo" || functionName === "fn.updateTodo") {
      return normalize(
        await todoService.request(normalizeTodoMutation(requestMessage.body), requestMessage.headers),
      );
    }

    if (functionName === "fn.getPlannerDashboard" || functionName === "fn.startFocusSession") {
      return normalize(await plannerService.request(requestMessage.body, requestMessage.headers));
    }

    return new Message({}, {
      ErrorInternal: {
        message: `Unknown function ${functionName}`,
      },
    });
  };

  const options = new ServerOptions();
  options.authRequired = false;
  options.onError = (error) => {
    console.error(error);
  };
  const telepactServer = new Server(schema, handler, options);

  const app = express();
  app.disable("x-powered-by");
  app.use("/api", express.raw({ type: "*/*", limit: "1mb" }));

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.post("/api", async (req, res, next) => {
    try {
      const requestBytes = new Uint8Array(req.body as Buffer);
      const response = await telepactServer.process(requestBytes);
      res.type("application/json");
      for (const [key, value] of Object.entries(response.headers)) {
        res.setHeader(key, String(value));
      }
      res.send(Buffer.from(response.bytes));
    } catch (error) {
      next(error);
    }
  });

  if (fs.existsSync(config.staticDir)) {
    app.use(express.static(config.staticDir));
    app.get(/^(?!\/api|\/health).*/, (_req, res) => {
      res.sendFile(path.join(config.staticDir, "index.html"));
    });
  }

  return app;
}

async function start(): Promise<void> {
  const config = loadConfig();
  const app = createApp(config);
  app.listen(config.port, () => {
    process.stdout.write(`bff listening on ${config.port}\n`);
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  start().catch((error) => {
    process.stderr.write(`${String(error)}\n`);
    process.exitCode = 1;
  });
}
