"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[3887],{3905:function(e,r,t){t.d(r,{Zo:function(){return l},kt:function(){return d}});var n=t(7294);function a(e,r,t){return r in e?Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[r]=t,e}function c(e,r){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);r&&(n=n.filter((function(r){return Object.getOwnPropertyDescriptor(e,r).enumerable}))),t.push.apply(t,n)}return t}function o(e){for(var r=1;r<arguments.length;r++){var t=null!=arguments[r]?arguments[r]:{};r%2?c(Object(t),!0).forEach((function(r){a(e,r,t[r])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):c(Object(t)).forEach((function(r){Object.defineProperty(e,r,Object.getOwnPropertyDescriptor(t,r))}))}return e}function p(e,r){if(null==e)return{};var t,n,a=function(e,r){if(null==e)return{};var t,n,a={},c=Object.keys(e);for(n=0;n<c.length;n++)t=c[n],r.indexOf(t)>=0||(a[t]=e[t]);return a}(e,r);if(Object.getOwnPropertySymbols){var c=Object.getOwnPropertySymbols(e);for(n=0;n<c.length;n++)t=c[n],r.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(a[t]=e[t])}return a}var i=n.createContext({}),s=function(e){var r=n.useContext(i),t=r;return e&&(t="function"==typeof e?e(r):o(o({},r),e)),t},l=function(e){var r=s(e.components);return n.createElement(i.Provider,{value:r},e.children)},u={inlineCode:"code",wrapper:function(e){var r=e.children;return n.createElement(n.Fragment,{},r)}},f=n.forwardRef((function(e,r){var t=e.components,a=e.mdxType,c=e.originalType,i=e.parentName,l=p(e,["components","mdxType","originalType","parentName"]),f=s(t),d=a,m=f["".concat(i,".").concat(d)]||f[d]||u[d]||c;return t?n.createElement(m,o(o({ref:r},l),{},{components:t})):n.createElement(m,o({ref:r},l))}));function d(e,r){var t=arguments,a=r&&r.mdxType;if("string"==typeof e||a){var c=t.length,o=new Array(c);o[0]=f;var p={};for(var i in r)hasOwnProperty.call(r,i)&&(p[i]=r[i]);p.originalType=e,p.mdxType="string"==typeof e?e:a,o[1]=p;for(var s=2;s<c;s++)o[s]=t[s];return n.createElement.apply(null,o)}return n.createElement.apply(null,t)}f.displayName="MDXCreateElement"},1395:function(e,r,t){t.r(r),t.d(r,{assets:function(){return i},contentTitle:function(){return o},default:function(){return u},frontMatter:function(){return c},metadata:function(){return p},toc:function(){return s}});var n=t(3117),a=(t(7294),t(3905));const c={},o="prepare",p={unversionedId:"cairo-1/testing/cheatcodes-reference/prepare",id:"cairo-1/testing/cheatcodes-reference/prepare",title:"prepare",description:"Prepares contract for deployment.",source:"@site/docs/cairo-1/06-testing/cheatcodes-reference/prepare.md",sourceDirName:"cairo-1/06-testing/cheatcodes-reference",slug:"/cairo-1/testing/cheatcodes-reference/prepare",permalink:"/protostar/docs/cairo-1/testing/cheatcodes-reference/prepare",draft:!1,editUrl:"https://github.com/software-mansion/protostar/tree/master/website/docs/cairo-1/06-testing/cheatcodes-reference/prepare.md",tags:[],version:"current",frontMatter:{},sidebar:"cairo1",previous:{title:"invoke",permalink:"/protostar/docs/cairo-1/testing/cheatcodes-reference/invoke"},next:{title:"start_prank",permalink:"/protostar/docs/cairo-1/testing/cheatcodes-reference/start_prank"}},i={},s=[],l={toc:s};function u(e){let{components:r,...t}=e;return(0,a.kt)("wrapper",(0,n.Z)({},l,t,{components:r,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"prepare"},(0,a.kt)("inlineCode",{parentName:"h1"},"prepare")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-cairo"},"fn prepare(class_hash: felt252, calldata: @Array::<felt252>) -> Result::<PreparedContract, felt252> nopanic;\n")),(0,a.kt)("p",null,"Prepares contract for deployment."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-cairo",metastring:'title="Example"',title:'"Example"'},"use result::ResultTrait;\nuse array::ArrayTrait;\n\n#[test]\nfn test_prepare() {\n    let class_hash = declare('mycontract').unwrap();\n\n    let mut calldata = ArrayTrait::new();\n    calldata.append(10);\n    calldata.append(11);\n    calldata.append(12);\n\n    let prepared_contract = prepare(class_hash, @calldata).unwrap();\n\n    // ...\n}\n")))}u.isMDXComponent=!0}}]);