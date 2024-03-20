# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support For `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking.

If the standalone TypeScript plugin doesn't feel fast enough to you, Volar has also implemented a [Take Over Mode](https://github.com/johnsoncodehk/volar/discussions/471#discussioncomment-1361669) that is more performant. You can enable it by the following steps:

1. Disable the built-in TypeScript Extension
   1. Run `Extensions: Show Built-in Extensions` from VSCode's command palette
   2. Find `TypeScript and JavaScript Language Features`, right click and select `Disable (Workspace)`
2. Reload the VSCode window by running `Developer: Reload Window` from the command palette.

## VS Code

### Conflicts on save

There also exist formatting rules at the editor level. If you want eslint errors to be fixed automatically when you save a file, then you probably want to disable editor formatting on save. In your `settings.json`:

```{json}
  "editor.formatOnSave": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
```

Or keep editor formatting for some languages (`@lang` in editor settings manager),

```{json}
  "editor.formatOnSave": true,
  "[vue]": {
    "editor.formatOnSave": false
  },
  "[typescript]": {
    "editor.formatOnSave": false
  }
```

### Finding `tsconfig.json`

Help VS Code finding your `tsconfig.json` (since it is not at the `${workspaceFolder}` level)

```{json}
  "eslint.workingDirectories": [
    { "directory": "FlOpEDT-front", "changeProcessCWD": true }
  ]
```
