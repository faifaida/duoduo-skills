# Changelog

## [2.0.0](https://github.com/faifaida/duoduo-skills/compare/v1.1.0...v2.0.0) (2026-08-22)


### ⚠ BREAKING CHANGES

* consolidate 23 standalone skills into 6 domain skills

### ✨ Features

* add 4 missing skills (gmail-imap-cleanup/journal-review-refine/notion-journal-split/reel-grid-pitfalls) + refresh manifest/catalog ([634ce98](https://github.com/faifaida/duoduo-skills/commit/634ce9801a46edc6721f9b97715bd23c3f97b887))
* add duo-rnote-t02-rewrite skill + refresh catalog/manifest ([e36b7f9](https://github.com/faifaida/duoduo-skills/commit/e36b7f95c8c77a51806ae09f70ea22809a8939b3))
* add duo-rnote-t02-rewrite skill + refresh catalog/manifest ([cb26289](https://github.com/faifaida/duoduo-skills/commit/cb2628972d7efceebc58c4ef4b5a453629a5edfb))
* add duo-rnote-t02-rewrite skill + refresh catalog/manifest ([de858a8](https://github.com/faifaida/duoduo-skills/commit/de858a8f2401f35d3f34b4c8d86d7729d55842ec))
* add Windows-only skills — duo-socialpublish-cdp, duo-content-weekly-workflow, duoduo-wear-poster ([d69bd05](https://github.com/faifaida/duoduo-skills/commit/d69bd054e6ba417663b8abf2b79ce4094e4797fc))
* add Windows-only skills — duo-socialpublish-cdp, duo-content-weekly-workflow, duoduo-wear-poster ([#9](https://github.com/faifaida/duoduo-skills/issues/9)) ([d69bd05](https://github.com/faifaida/duoduo-skills/commit/d69bd054e6ba417663b8abf2b79ce4094e4797fc))
* consolidate 23 standalone skills into 6 domain skills ([3a4f616](https://github.com/faifaida/duoduo-skills/commit/3a4f61684bd54cd046d217f62fab69337e9b1bdd))
* merge 2 orphan skills (duo-video-script, duoduowear-illustrations) from workbuddy-skills; single source of truth ([863cd2f](https://github.com/faifaida/duoduo-skills/commit/863cd2ff2e114d4d70205ec70cb086e8a4a056b0))
* **shifei-video-edit:** 字幕+音乐+封面重混方法 (V06t) ([bea9c3c](https://github.com/faifaida/duoduo-skills/commit/bea9c3c5c5d03ef9d551e567de606354794ccf33))
* **shifei:** subtitle number-atomization rule (merge_numbers) from V21c ([c6e6c45](https://github.com/faifaida/duoduo-skills/commit/c6e6c45bc4559d3c6b2d579f6cf83b63f67e9349))
* **skills:** 补全 31 个验证过的完整技能 + 过程版本 + 转 public ([9477bca](https://github.com/faifaida/duoduo-skills/commit/9477bcac4ccfe45e5e819da1f5671a838403f134))


### 🐛 Bug Fixes

* **ci:** install pyyaml before validate-skills ([245227c](https://github.com/faifaida/duoduo-skills/commit/245227c03044cd1c314b50f3d59e0d8796b671a7))
* remove leftover duoduo-voice-deai standalone source (merged into duo-voice-deai) ([eb24bbb](https://github.com/faifaida/duoduo-skills/commit/eb24bbb19496e8943e93908472b1676e6d9c7a87))
* **shifei-video-edit:** V21b 字幕 jieba 按词断句规则沉淀(ASR盲切拆词坑) ([4c1b41a](https://github.com/faifaida/duoduo-skills/commit/4c1b41ae1c55c5aa7575127a3b9a310766dc12d9))
* **shifei-video-edit:** 修正去重双闸+补 V07b 程序化构建技术备忘 ([1f1930f](https://github.com/faifaida/duoduo-skills/commit/1f1930f347fcabf54611ed266b09dfbcfdd4e775))
* **shifei-video-edit:** 加开头钩子快剪规则(V07c) ([56e4b77](https://github.com/faifaida/duoduo-skills/commit/56e4b77ef4026ac05b810eba6b1ab782520daa4b))
* **weekly-review-calendar:** 固化月相四阶段→主题轴映射(原文照抄) + 本周等式置顶输出铁律(2026-08-17) ([5a30f31](https://github.com/faifaida/duoduo-skills/commit/5a30f316201f124ce29f1447ce4391c1c5550ec8))


### 📚 Documentation

* drop daily-diary-skill from catalog (merged into duo-life-tasks) ([f54c6db](https://github.com/faifaida/duoduo-skills/commit/f54c6db4aeef1d174b33790f426d68ed26bdb57b))


### ♻️ Refactor

* fold T02 rewrite into duo-knowledge-classify (rm standalone skill) ([a5346c7](https://github.com/faifaida/duoduo-skills/commit/a5346c7e62136cb9fa3e143127bcc29453f99cbd))
* fold T02 rewrite into duo-knowledge-classify (rm standalone skill) ([b7e0076](https://github.com/faifaida/duoduo-skills/commit/b7e0076d27b40c90bcef46fb1e96928222c1990c))
* fold T02 rewrite into duo-knowledge-classify (rm standalone skill) ([ec9ced0](https://github.com/faifaida/duoduo-skills/commit/ec9ced0ab3b803620060c4fed2d5b4cc7da27d4d))
* fold T02 rewrite into duo-knowledge-classify (rm standalone skill) ([bb1e461](https://github.com/faifaida/duoduo-skills/commit/bb1e461db539e0ab99d3dc9fb5e3b570a96f665f))
* fold T02 rewrite into duo-knowledge-classify (rm standalone skill) ([c9c2811](https://github.com/faifaida/duoduo-skills/commit/c9c281181e8f02f25846ce2acf3940a263ae0644))
* remove duoduo-design-system from collection (now standalone repo faifaida/duoduo-design-system is single source) ([cddf280](https://github.com/faifaida/duoduo-skills/commit/cddf280bd00afaca2de38f59da5b591b0369a1b1))


### 🔧 Chores

* regenerate skills-manifest.json after removing daily-diary-skill ([f01a36c](https://github.com/faifaida/duoduo-skills/commit/f01a36cf5f01d9086cd8cfa40207362b86e74c6f))
* remove stale daily-diary-skill (content merged into duo-life-tasks) ([de84b5e](https://github.com/faifaida/duoduo-skills/commit/de84b5eaed57ec2b9b65e41dca1c49810a38ade1))
* 扩展邮箱清理为 Gmail+QQ 统一规范 + 新增脚本 + 周自动化配套 ([08bef54](https://github.com/faifaida/duoduo-skills/commit/08bef54a51c71d3d64bc156326933d9e08abddf5))
* 扩展邮箱清理为 Gmail+QQ 统一规范 + 新增脚本 + 周自动化配套 ([fc69181](https://github.com/faifaida/duoduo-skills/commit/fc691812a2d5df6c0766cd082dcc40208b26aa10))
* 扩展邮箱清理为 Gmail+QQ 统一规范 + 新增脚本 + 周自动化配套 ([b7b7b30](https://github.com/faifaida/duoduo-skills/commit/b7b7b301484a66b82a699e4d425d5752b8b93b7f))
