# ts-codegen

Minimal TypeScript Telepact example that shows both the generated client and the
generated server bindings wired into the runtime library.

Browse the files:

- [`api/greet.telepact.yaml`](./api/greet.telepact.yaml) - Telepact schema
- [`gen/genTypes.ts`](./gen/genTypes.ts) - committed generated bindings
- [`server.ts`](./server.ts) - generated server handler wired into Telepact
- [`test_example.ts`](./test_example.ts) - generated client wired into Telepact
- [`Makefile`](./Makefile) - local run target, including codegen

Run it:

```bash
make run
```

The committed generated bindings also type-check in strict modern ESM setups
without special compiler concessions:

```bash
npm run build
npm run build:bundler
```
