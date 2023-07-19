"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[6413],{3905:function(e,t,n){n.d(t,{Zo:function(){return p},kt:function(){return u}});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function c(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},o=Object.keys(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var l=a.createContext({}),s=function(e){var t=a.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},p=function(e){var t=s(e.components);return a.createElement(l.Provider,{value:t},e.children)},m={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},d=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,o=e.originalType,l=e.parentName,p=c(e,["components","mdxType","originalType","parentName"]),d=s(n),u=r,k=d["".concat(l,".").concat(u)]||d[u]||m[u]||o;return n?a.createElement(k,i(i({ref:t},p),{},{components:n})):a.createElement(k,i({ref:t},p))}));function u(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var o=n.length,i=new Array(o);i[0]=d;var c={};for(var l in t)hasOwnProperty.call(t,l)&&(c[l]=t[l]);c.originalType=e,c.mdxType="string"==typeof e?e:r,i[1]=c;for(var s=2;s<o;s++)i[s]=n[s];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}d.displayName="MDXCreateElement"},1263:function(e,t,n){n.r(t),n.d(t,{assets:function(){return l},contentTitle:function(){return i},default:function(){return m},frontMatter:function(){return o},metadata:function(){return c},toc:function(){return s}});var a=n(3117),r=(n(7294),n(3905));const o={},i="Understanding Cairo packages",c={unversionedId:"cairo-1/understanding-cairo-packages",id:"cairo-1/understanding-cairo-packages",title:"Understanding Cairo packages",description:"There are several requirements that Cairo packages have to follow. These are explained in the following sections.",source:"@site/docs/cairo-1/04-understanding-cairo-packages.md",sourceDirName:"cairo-1",slug:"/cairo-1/understanding-cairo-packages",permalink:"/protostar/docs/cairo-1/understanding-cairo-packages",draft:!1,editUrl:"https://github.com/software-mansion/protostar/tree/master/website/docs/cairo-1/04-understanding-cairo-packages.md",tags:[],version:"current",sidebarPosition:4,frontMatter:{},sidebar:"cairo1",previous:{title:"Project initialization",permalink:"/protostar/docs/cairo-1/project-initialization"},next:{title:"Understanding protostar.toml",permalink:"/protostar/docs/cairo-1/protostar-toml"}},l={},s=[{value:"Dependencies management",id:"dependencies-management",level:2},{value:"Modules",id:"modules",level:2},{value:"Packages",id:"packages",level:2},{value:"<code>Scarb.toml</code>",id:"scarbtoml",level:3},{value:"<code>lib.cairo</code>",id:"libcairo",level:3},{value:"Package with multiple modules",id:"package-with-multiple-modules",level:3},{value:"Project with multiple contracts",id:"project-with-multiple-contracts",level:2},{value:"Multi-contract project structure",id:"multi-contract-project-structure",level:3},{value:"Testing multi-contract projects",id:"testing-multi-contract-projects",level:3},{value:"Packages and modules names considerations",id:"packages-and-modules-names-considerations",level:2}],p={toc:s};function m(e){let{components:t,...n}=e;return(0,r.kt)("wrapper",(0,a.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"understanding-cairo-packages"},"Understanding Cairo packages"),(0,r.kt)("p",null,"There are several requirements that Cairo packages have to follow. These are explained in the following sections."),(0,r.kt)("p",null,"You can refer to ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/starkware-libs/cairo/tree/main/docs/reference"},"official Cairo documentation")," for\nmore details. "),(0,r.kt)("p",null,"Keep in mind that Protostar does not support ",(0,r.kt)("inlineCode",{parentName:"p"},"cairo_project.toml"),".\nIt uses ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb"},"Scarb")," and its ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/docs/reference/manifest"},"manifest files")," instead."),(0,r.kt)("h2",{id:"dependencies-management"},"Dependencies management"),(0,r.kt)("p",null,"Protostar uses ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb"},"Scarb")," and its ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/docs/reference/manifest"},"manifest files")," to manage dependencies in your project.\nIn order to use Protostar with Cairo 1, you must have Scarb executable added to the ",(0,r.kt)("inlineCode",{parentName:"p"},"PATH")," environment variable.\nThe ",(0,r.kt)("inlineCode",{parentName:"p"},"PATH")," variable is a list of directories that your system searches for executables."),(0,r.kt)("p",null,"To learn how to manage dependencies with Scarb, check ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/docs/reference/specifying-dependencies"},"the documentation"),"."),(0,r.kt)("admonition",{type:"info"},(0,r.kt)("p",{parentName:"admonition"},"The name of your package is always the value\nof the ",(0,r.kt)("inlineCode",{parentName:"p"},"name")," key in the ",(0,r.kt)("inlineCode",{parentName:"p"},"[package]")," section of your ",(0,r.kt)("inlineCode",{parentName:"p"},"Scarb.toml"),". ")),(0,r.kt)("h2",{id:"modules"},"Modules"),(0,r.kt)("p",null,"A module consists of one or more Cairo files, usually organized in a single directory. To define a module, create\na ",(0,r.kt)("inlineCode",{parentName:"p"},".cairo")," file named like the module and define components of this module with the ",(0,r.kt)("inlineCode",{parentName:"p"},"mod")," keyword."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"my_module/\n\u251c\u2500\u2500 a.cairo\n\u251c\u2500\u2500 b.cairo\n\u2514\u2500\u2500 c.cairo\nmy_module.cairo\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="my_module.cairo"',title:'"my_module.cairo"'},"mod a;\nmod b;\nmod c;\n")),(0,r.kt)("p",null,"Alternatively, modules can be defined within a file using"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="my_module.cairo"',title:'"my_module.cairo"'},"mod my_module {\n    fn function_a() -> ();\n    // ...\n}\n")),(0,r.kt)("h2",{id:"packages"},"Packages"),(0,r.kt)("p",null,"Package consist of multiple modules and must define ",(0,r.kt)("inlineCode",{parentName:"p"},"Scarb.toml")," and ",(0,r.kt)("inlineCode",{parentName:"p"},"src/lib.cairo")," files."),(0,r.kt)("admonition",{type:"info"},(0,r.kt)("p",{parentName:"admonition"},"Some other tools and resources,\nincluding ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/starkware-libs/cairo/tree/main/docs/reference"},"official Cairo documentation"),', use the\nterm "crates" for packages.')),(0,r.kt)("h3",{id:"scarbtoml"},(0,r.kt)("inlineCode",{parentName:"h3"},"Scarb.toml")),(0,r.kt)("p",null,"It is a ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/docs/reference/manifest"},"Scarb's manifest files"),"\ncontaining dependencies for your package."),(0,r.kt)("p",null,"Example content of this file:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="Scarb.toml"',title:'"Scarb.toml"'},'[package]\nname = "my_package"\nversion = "0.1.0"\n\n[dependencies]\n')),(0,r.kt)("h3",{id:"libcairo"},(0,r.kt)("inlineCode",{parentName:"h3"},"lib.cairo")),(0,r.kt)("p",null,"It is the root of the package tree, and it ",(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("em",{parentName:"strong"},"must"))," be placed inside ",(0,r.kt)("inlineCode",{parentName:"p"},"src")," folder.\nHere you can define functions, declare used modules, etc."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="lib.cairo"',title:'"lib.cairo"'},"mod my_module;\nmod my_other_module;\n")),(0,r.kt)("h3",{id:"package-with-multiple-modules"},"Package with multiple modules"),(0,r.kt)("p",null,"The module system in Cairo is inspired by\n",(0,r.kt)("a",{parentName:"p",href:"https://doc.rust-lang.org/rust-by-example/mod/split.html"},"Rust's")," one.\nAn example package with multiple modules:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"my_project/\n\u251c\u2500\u2500 src/\n\u2502   \u251c\u2500\u2500 mod1/\n\u2502   \u2502   \u2514\u2500\u2500 functions.cairo\n\u2502   \u251c\u2500\u2500 mod1.cairo\n\u2502   \u251c\u2500\u2500 utils.cairo\n\u2502   \u2514\u2500\u2500 lib.cairo\n\u2514\u2500\u2500 Scarb.toml\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="lib.cairo"',title:'"lib.cairo"'},"mod mod1;\nmod utils;\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="mod1.cairo"',title:'"mod1.cairo"'},"mod functions;\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="utils.cairo"',title:'"utils.cairo"'},"fn returns_two() -> felt252 {\n    2\n}\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="mod1/functions.cairo"',title:'"mod1/functions.cairo"'},"fn returns_three() -> felt252 {\n    3\n}\n")),(0,r.kt)("p",null,"You can now use the defined functions with\n",(0,r.kt)("inlineCode",{parentName:"p"},"my_package::mod1::functions::returns_three()")," and ",(0,r.kt)("inlineCode",{parentName:"p"},"my_package::utils::returns_two()"),"."),(0,r.kt)("h2",{id:"project-with-multiple-contracts"},"Project with multiple contracts"),(0,r.kt)("p",null,"Due to limitations of the Cairo 1 compiler, having multiple contracts defined in the package will cause\nthe ",(0,r.kt)("inlineCode",{parentName:"p"},"protostar build")," command and other commands to fail."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"That is, having projects structured like this is not valid and will not work correctly.")),(0,r.kt)("h3",{id:"multi-contract-project-structure"},"Multi-contract project structure"),(0,r.kt)("p",null,"Each contract must be defined in the separate package: a different directory with separate ",(0,r.kt)("inlineCode",{parentName:"p"},"Scarb.toml"),"\nand ",(0,r.kt)("inlineCode",{parentName:"p"},"src/lib.cairo")," files defined."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"my_project/\n\u251c\u2500\u2500 package1/\n\u2502   \u251c\u2500\u2500 src/\n\u2502   \u2502   \u251c\u2500\u2500 contract/\n\u2502   \u2502   \u2502   \u2514\u2500\u2500 hello_starknet.cairo\n\u2502   \u2502  ...\n\u2502   \u2502   \u251c\u2500\u2500 contract.cairo\n\u2502   \u2502   \u2514\u2500\u2500 lib.cairo\n\u2502   \u2514\u2500\u2500 Scarb.toml\n\u251c\u2500\u2500 package2/\n\u2502   \u251c\u2500\u2500 src/\n\u2502   \u2502   \u251c\u2500\u2500 contract/\n\u2502   \u2502   \u2502   \u2514\u2500\u2500 other_contract.cairo\n\u2502   \u2502  ...\n\u2502   \u2502   \u251c\u2500\u2500 contract.cairo\n\u2502   \u2502   \u2514\u2500\u2500 lib.cairo\n\u2502   \u2514\u2500\u2500 Scarb.toml\n...\n\u251c\u2500\u2500 src/\n\u2502   \u2514\u2500\u2500 lib.cairo\n\u251c\u2500\u2500 Scarb.toml\n\u2514\u2500\u2500 protostar.toml\n")),(0,r.kt)("admonition",{type:"caution"},(0,r.kt)("p",{parentName:"admonition"},"Notice that the whole project itself is a package too.\nThis is due to the fact that ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/"},"Scarb"),"\ndoes not support workspaces yet. If you do not need to include any code\nin the top level package, just leave the ",(0,r.kt)("inlineCode",{parentName:"p"},"my_project/src/lib.cairo")," file empty.")),(0,r.kt)("p",null,"Define each contract in the ",(0,r.kt)("inlineCode",{parentName:"p"},"[contracts]")," section of the protostar.toml."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="protostar.toml"',title:'"protostar.toml"'},'# ...\n[contracts]\nhello_starknet = ["package1/src"]\nother_contract = ["package2/src"]\n')),(0,r.kt)("p",null,"Remember to include the packages as ",(0,r.kt)("a",{parentName:"p",href:"https://docs.swmansion.com/scarb/docs/reference/specifying-dependencies"},"dependencies")," in ",(0,r.kt)("inlineCode",{parentName:"p"},"my_project/Scarb.toml"),"."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="my_project/Scarb.toml"',title:'"my_project/Scarb.toml"'},'[package]\nname = "my_package"\nversion = "0.1.0"\n\n[dependencies]\npackage1 = { path = "package1" }\npackage2 = { path = "package2" }\n')),(0,r.kt)("h3",{id:"testing-multi-contract-projects"},"Testing multi-contract projects"),(0,r.kt)("p",null,"For example, to test function ",(0,r.kt)("inlineCode",{parentName:"p"},"returns_two")," defined in the ",(0,r.kt)("inlineCode",{parentName:"p"},"package1/business_logic/utils.cairo")," write"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="my_project/test_package1.cairo"',title:'"my_project/test_package1.cairo"'},"#[test]\nfn test_returns_two() {\n    assert(package1::business_logic::utils::returns_two() == 2, 'Should return 2');\n}\n")),(0,r.kt)("p",null,"Or using the ",(0,r.kt)("inlineCode",{parentName:"p"},"use path::to::mod")," syntax"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="my_project/test_package2.cairo"',title:'"my_project/test_package2.cairo"'},"use package1::business_logic::utils::returns_two;\n\n#[test]\nfn test_returns_two() {\n    assert(returns_two() == 2, 'Should return 2');\n}\n")),(0,r.kt)("p",null,"Make sure that the ",(0,r.kt)("inlineCode",{parentName:"p"},"path::to::the::module")," is correct for your package structure."),(0,r.kt)("p",null,"For more details on how to test contracts, see ",(0,r.kt)("a",{parentName:"p",href:"/protostar/docs/cairo-1/testing/"},"this page"),"."),(0,r.kt)("h2",{id:"packages-and-modules-names-considerations"},"Packages and modules names considerations"),(0,r.kt)("p",null,"The name must be a valid Cairo identifier which means:"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"it must use only ASCII alphanumeric characters or underscores"),(0,r.kt)("li",{parentName:"ul"},"it cannot start with a digit"),(0,r.kt)("li",{parentName:"ul"},"it cannot be empty"),(0,r.kt)("li",{parentName:"ul"},"it cannot be a valid Cairo keyword or a single underscore (",(0,r.kt)("inlineCode",{parentName:"li"},"_"),")")))}m.isMDXComponent=!0}}]);