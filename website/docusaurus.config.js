// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Protostar",
  tagline: "StarkNet smart contract development toolchain",
  url: "https://your-docusaurus-test-site.com",
  baseUrl: "/protostar/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",
  organizationName: "software-mansion",
  projectName: "protostar",
  trailingSlash: false,
  deploymentBranch: "gh-pages",

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          editUrl: ({ docPath }) =>
            `https://github.com/software-mansion/protostar/tree/master/website/docs/${docPath}`,
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "Protostar",
        logo: {
          alt: "Protostar",
          src: "img/protostar-logo--dark.png",
          srcDark: "img/protostar-logo--light.png",
        },
        items: [
          {
            type: "docSidebar",
            position: "left",
            sidebarId: "tutorials",
            label: "Tutorials",
          },
          {
            href: "https://github.com/software-mansion/protostar",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              {
                label: "Tutorials",
                to: "/docs/tutorials/introduction",
              },
            ],
          },
          // {
          //   title: 'Community',
          //   items: [
          //     //   {
          //     //     label: 'Discord',
          //     //     href: 'https://discordapp.com/invite/docusaurus',
          //     //   },
          //   ],
          // },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Protostar, Inc. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ["toml"]
      },
    }),
};

module.exports = config;
