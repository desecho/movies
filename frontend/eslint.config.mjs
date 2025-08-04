import { fixupConfigRules } from "@eslint/compat";
import tsParser from "@typescript-eslint/parser";
import parser from "vue-eslint-parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import globals from "globals";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...fixupConfigRules(compat.extends(
    "eslint:recommended",
    "plugin:eslint-comments/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "plugin:vue/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:@typescript-eslint/strict",
    "prettier",
)), {
    languageOptions: {
        ecmaVersion: 5,
        sourceType: "module",
        globals: {
            ...globals.browser,
        },
        parserOptions: {
            project: ["./tsconfig.json"],
            extraFileExtensions: [".vue"],
            projectService: true
        },
    },

    settings: {
        "import/resolver": {
            typescript: {
                project: "./tsconfig.json",
            },
        },
    },

    rules: {
        "object-shorthand": "error",
        "no-param-reassign": "error",
        "no-proto": "error",
        "no-implicit-coercion": "error",
        "no-iterator": "error",
        "no-label-var": "error",
        "no-labels": "error",
        "no-lone-blocks": "error",
        "no-lonely-if": "error",
        "operator-assignment": "error",
        "no-multi-assign": "error",
        "no-negated-condition": "error",
        "no-nested-ternary": "error",
        "no-new": "error",
        "no-new-func": "error",
        "no-floating-decimal": "error",
        "no-extra-label": "error",
        "no-eval": "error",
        "no-alert": "error",
        "no-bitwise": "error",
        "no-unused-private-class-members": "error",
        "no-unreachable-loop": "error",
        "no-unmodified-loop-condition": "error",
        "no-template-curly-in-string": "error",
        "no-self-compare": "error",
        "no-promise-executor-return": "error",
        "no-constructor-return": "error",
        "no-constant-binary-expression": "error",
        "no-await-in-loop": "error",
        eqeqeq: "error",
        "func-style": ["error", "declaration"],
        "default-case-last": "error",
        "grouped-accessor-pairs": "error",
        "require-atomic-updates": "error",
        "array-callback-return": "error",
        "multiline-comment-style": ["error", "bare-block"],
        "prefer-arrow-callback": "error",
        "prefer-exponentiation-operator": "error",
        "prefer-const": "error",
        "prefer-named-capture-group": "error",
        "prefer-numeric-literals": "error",
        "prefer-object-has-own": "error",
        "prefer-object-spread": "error",
        "prefer-promise-reject-errors": "error",
        "prefer-regex-literals": "error",
        "prefer-rest-params": "error",
        "prefer-spread": "error",
        "prefer-template": "error",
        "no-return-await": "error",
        "no-script-url": "error",
        radix: "error",
        "no-octal-escape": "error",
        curly: "error",
        "no-sequences": "error",
        "require-unicode-regexp": "error",
        "no-undef-init": "error",
        "no-unneeded-ternary": "error",
        "no-return-assign": "error",
        // conflicts with Prettier
        // "quote-props": ["error", "consistent-as-needed"],
        "spaced-comment": "error",
        "symbol-description": "error",
        yoda: "error",
        "no-useless-rename": "error",
        "no-useless-return": "error",
        "no-var": "error",
        "no-useless-computed-key": "error",
        "no-useless-concat": "error",
        "no-useless-call": "error",
        "no-div-regex": "error",
        "no-else-return": "error",
        "accessor-pairs": "error",
        "capitalized-comments": "error",

        "max-len": ["error", {
            code: 119,
        }],

        "sort-imports": ["error", {
            ignoreCase: true,
            ignoreDeclarationSort: true,
        }],

        strict: ["error", "never"],
        "max-statements-per-line": "error",
        "require-jsdoc": "off",

        camelcase: ["error", {
            allow: ["jwt_decode"],
        }],

        "@typescript-eslint/unbound-method": "off",
        "@typescript-eslint/default-param-last": "error",
        "@/lines-between-class-members": "error",
        "@typescript-eslint/no-loop-func": "error",
        "@typescript-eslint/no-shadow": "error",
        "@typescript-eslint/no-unused-expressions": "error",
        "@typescript-eslint/no-use-before-define": "error",
        "@typescript-eslint/consistent-type-exports": "error",
        "@typescript-eslint/consistent-type-imports": "error",
        "@typescript-eslint/explicit-function-return-type": "error",
        "@typescript-eslint/explicit-member-accessibility": "error",
        "@typescript-eslint/explicit-module-boundary-types": "error",
        "@typescript-eslint/member-ordering": "error",
        "@typescript-eslint/method-signature-style": "error",
        "@typescript-eslint/no-confusing-void-expression": "error",
        "@typescript-eslint/no-redundant-type-constituents": "error",
        "@typescript-eslint/no-require-imports": "error",
        "@typescript-eslint/no-unnecessary-qualifier": "error",
        "@typescript-eslint/no-useless-empty-export": "error",
        // "@typescript-eslint/strict-boolean-expressions": "error",
        "@typescript-eslint/prefer-readonly": "error",
        "@typescript-eslint/prefer-regexp-exec": "error",
        "@typescript-eslint/promise-function-async": "error",
        "@typescript-eslint/require-array-sort-compare": "error",
        "@typescript-eslint/switch-exhaustiveness-check": "error",
        "import/no-unresolved": "error",
        "import/newline-after-import": "error",
        "import/no-unassigned-import": "error",

        "import/order": ["error", {
            groups: [
                "builtin",
                "external",
                "internal",
                "type",
                "unknown",
                "parent",
                "sibling",
                "index",
                "object",
            ],

            "newlines-between": "always",

            alphabetize: {
                order: "asc",
                caseInsensitive: true,
            },
        }],

        "import/first": "error",

        "import/no-useless-path-segments": ["error", {
            noUselessIndex: true,
        }],

        "import/no-deprecated": "error",

        "import/no-extraneous-dependencies": ["error", {
            devDependencies: false,
            optionalDependencies: false,
            peerDependencies: false,
            bundledDependencies: false,
        }],

        "eslint-comments/no-unused-disable": "error",

        "vue/block-lang": ["error", {
            script: {
                lang: "ts",
                allowNoLang: false,
            },
        }],
    },
}, {
    files: ["**/*.ts"],

    languageOptions: {
        parser: tsParser,
    },
}, {
    files: ["**/*.vue"],

    languageOptions: {
        parser: parser,
        ecmaVersion: 5,
        sourceType: "module",

        parserOptions: {
            parser: "@typescript-eslint/parser",
        },
    },
}];
