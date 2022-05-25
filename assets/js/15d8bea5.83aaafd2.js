"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[378],{3905:function(t,e,n){n.d(e,{Zo:function(){return c},kt:function(){return d}});var r=n(7294);function o(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function i(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(t);e&&(r=r.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,r)}return n}function a(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?i(Object(n),!0).forEach((function(e){o(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}function l(t,e){if(null==t)return{};var n,r,o=function(t,e){if(null==t)return{};var n,r,o={},i=Object.keys(t);for(r=0;r<i.length;r++)n=i[r],e.indexOf(n)>=0||(o[n]=t[n]);return o}(t,e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);for(r=0;r<i.length;r++)n=i[r],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(t,n)&&(o[n]=t[n])}return o}var p=r.createContext({}),s=function(t){var e=r.useContext(p),n=e;return t&&(n="function"==typeof t?t(e):a(a({},e),t)),n},c=function(t){var e=s(t.components);return r.createElement(p.Provider,{value:e},t.children)},u={inlineCode:"code",wrapper:function(t){var e=t.children;return r.createElement(r.Fragment,{},e)}},m=r.forwardRef((function(t,e){var n=t.components,o=t.mdxType,i=t.originalType,p=t.parentName,c=l(t,["components","mdxType","originalType","parentName"]),m=s(n),d=o,f=m["".concat(p,".").concat(d)]||m[d]||u[d]||i;return n?r.createElement(f,a(a({ref:e},c),{},{components:n})):r.createElement(f,a({ref:e},c))}));function d(t,e){var n=arguments,o=e&&e.mdxType;if("string"==typeof t||o){var i=n.length,a=new Array(i);a[0]=m;var l={};for(var p in e)hasOwnProperty.call(e,p)&&(l[p]=e[p]);l.originalType=t,l.mdxType="string"==typeof t?t:o,a[1]=l;for(var s=2;s<i;s++)a[s]=n[s];return r.createElement.apply(null,a)}return r.createElement.apply(null,n)}m.displayName="MDXCreateElement"},9509:function(t,e,n){n.r(e),n.d(e,{assets:function(){return c},contentTitle:function(){return p},default:function(){return d},frontMatter:function(){return l},metadata:function(){return s},toc:function(){return u}});var r=n(7462),o=n(3366),i=(n(7294),n(3905)),a=["components"],l={sidebar_label:"Project initialization (1 min)"},p="Project initialization",s={unversionedId:"tutorials/project-initialization",id:"tutorials/project-initialization",title:"Project initialization",description:"To create a new project run:",source:"@site/docs/tutorials/03-project-initialization.md",sourceDirName:"tutorials",slug:"/tutorials/project-initialization",permalink:"/protostar/docs/tutorials/project-initialization",editUrl:"https://github.com/software-mansion/protostar/tree/master/website/docs/tutorials/03-project-initialization.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_label:"Project initialization (1 min)"},sidebar:"tutorials",previous:{title:"Installation (1 min)",permalink:"/protostar/docs/tutorials/installation"},next:{title:"Compilation (1 min)",permalink:"/protostar/docs/tutorials/guides/compiling"}},c={},u=[{value:"Adapting an existing project to the Protostar project",id:"adapting-an-existing-project-to-the-protostar-project",level:3},{value:"<code>protostar.toml</code>",id:"protostartoml",level:2},{value:"Project configuration",id:"project-configuration",level:3},{value:"Command configuration",id:"command-configuration",level:3},{value:"Configuration profiles",id:"configuration-profiles",level:3}],m={toc:u};function d(t){var e=t.components,n=(0,o.Z)(t,a);return(0,i.kt)("wrapper",(0,r.Z)({},m,n,{components:e,mdxType:"MDXLayout"}),(0,i.kt)("h1",{id:"project-initialization"},"Project initialization"),(0,i.kt)("p",null,"To create a new project run:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-console"},"protostar init\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-console",metastring:'title="Protostar configuration step."',title:'"Protostar',configuration:!0,'step."':!0},"libraries directory name (lib):\n")),(0,i.kt)("h3",{id:"adapting-an-existing-project-to-the-protostar-project"},"Adapting an existing project to the Protostar project"),(0,i.kt)("p",null,"Protostar project must be a git repository and have ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar.toml")," file. You can adapt your project manually or by running ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar init --existing"),"."),(0,i.kt)("h1",{id:"project-structure"},"Project structure"),(0,i.kt)("p",null,"The result of running ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar init")," is a configuration file ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar.toml"),", example files, and the following 3 directories:"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("inlineCode",{parentName:"li"},"src")," \u2014 A directory for your code."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("inlineCode",{parentName:"li"},"lib")," \u2014 A default directory for an external dependencies."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("inlineCode",{parentName:"li"},"tests")," \u2014 A directory storing tests.")),(0,i.kt)("h2",{id:"protostartoml"},(0,i.kt)("inlineCode",{parentName:"h2"},"protostar.toml")),(0,i.kt)("h3",{id:"project-configuration"},"Project configuration"),(0,i.kt)("p",null,"Project configuration is required."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="protostar.toml"',title:'"protostar.toml"'},'["protostar.config"]\nprotostar_version = "0.1.0"\n\n["protostar.project"]\nlibs_path = "./lib"         # a path to the dependency directory\n\n# This section is explained in the "Project compilation" guide.\n["protostar.contracts"]\nmain = [\n  "./src/main.cairo",\n]\n\n')),(0,i.kt)("h3",{id:"command-configuration"},"Command configuration"),(0,i.kt)("p",null,"Not required arguments can be configured in the ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar.toml"),". It allows you to avoid passing arguments every time you run a command. Protostar checks ",(0,i.kt)("inlineCode",{parentName:"p"},'["protostar.COMMAND_NAME"]')," section and searches an attribute matching an argument name with underscores (",(0,i.kt)("inlineCode",{parentName:"p"},"_"),") in place of dashes (",(0,i.kt)("inlineCode",{parentName:"p"},"-"),"), for example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="protostar.toml"',title:'"protostar.toml"'},'# ...\n\n["protostar.build"]\ncairo_path = ["./lib/cairo_contracts/src"]\n')),(0,i.kt)("p",null,"If you want to configure an argument that is not tied to any command or an argument that is shared across many commands (e.g. ",(0,i.kt)("inlineCode",{parentName:"p"},"cairo-path"),"), specify it in the ",(0,i.kt)("inlineCode",{parentName:"p"},'["protostar.shared_command_configs"]')," section. This is useful if you want to specify the same ",(0,i.kt)("inlineCode",{parentName:"p"},"cairo-path")," for ",(0,i.kt)("inlineCode",{parentName:"p"},"build")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"test")," commands as demonstrated on the following example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="protostar.toml"',title:'"protostar.toml"'},'# ...\n\n["protostar.shared_command_configs"]\ncairo_path = ["./lib/cairo_contracts/src"]\n')),(0,i.kt)("div",{className:"admonition admonition-info alert alert--info"},(0,i.kt)("div",{parentName:"div",className:"admonition-heading"},(0,i.kt)("h5",{parentName:"div"},(0,i.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,i.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,i.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M7 2.3c3.14 0 5.7 2.56 5.7 5.7s-2.56 5.7-5.7 5.7A5.71 5.71 0 0 1 1.3 8c0-3.14 2.56-5.7 5.7-5.7zM7 1C3.14 1 0 4.14 0 8s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm1 3H6v5h2V4zm0 6H6v2h2v-2z"}))),"info")),(0,i.kt)("div",{parentName:"div",className:"admonition-content"},(0,i.kt)("p",{parentName:"div"},"You can't specify the ",(0,i.kt)("inlineCode",{parentName:"p"},"profile")," argument in the ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar.toml"),"."))),(0,i.kt)("h3",{id:"configuration-profiles"},"Configuration profiles"),(0,i.kt)("p",null,"Configuration profiles provide a way to easily switch between Protostar configurations. This is especially useful for configuring StarkNet networks. Profiles inherit values from non-profiled configuration. In order to create a configuration profile, add a new section in ",(0,i.kt)("inlineCode",{parentName:"p"},"protostar.toml")," with the following naming convention:",(0,i.kt)("br",null),"  ",(0,i.kt)("inlineCode",{parentName:"p"},'["profile.PROFILE_NAME.protostar.COMMAND_NAME"]'),"."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-toml",metastring:'title="protostar.toml"',title:'"protostar.toml"'},'# ...\n["profile.ci.protostar.shared_command_configs"]\nno_color = true\n')),(0,i.kt)("p",null,"Then, run Protostar with the ",(0,i.kt)("inlineCode",{parentName:"p"},"--profile")," (or ",(0,i.kt)("inlineCode",{parentName:"p"},"-p"),") argument:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-shell"},"protostar -p ci ...\n\n")))}d.isMDXComponent=!0}}]);