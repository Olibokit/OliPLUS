define("ace/mode/dockerfile_highlight_rules", ["require", "exports", "module"], function(require, exports, module) {
  const oop = require("ace/lib/oop");
  const TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

  const DockerfileHighlightRules = function() {
    const keywords = (
      "FROM|AS|RUN|CMD|LABEL|MAINTAINER|EXPOSE|ENV|ADD|COPY|ENTRYPOINT|" +
      "VOLUME|USER|WORKDIR|ARG|ONBUILD|STOPSIGNAL|HEALTHCHECK|SHELL"
    );

    this.$rules = {
      start: [
        {
          token: "keyword.control.dockerfile",
          regex: `\\b(${keywords})\\b`
        },
        {
          token: "variable.parameter.dockerfile",
          regex: "\\$\\{?[\\w_]+\\}?"
        },
        {
          token: "comment.line.number-sign.dockerfile",
          regex: "#.*$"
        },
        {
          token: "string.quoted.double.dockerfile",
          regex: '".*?"'
        },
        {
          token: "string.quoted.single.dockerfile",
          regex: "'.*?'"
        },
        {
          token: "constant.language.boolean.dockerfile",
          regex: "\\b(true|false|on|off)\\b"
        },
        {
          token: "constant.numeric.dockerfile",
          regex: "\\b\\d+(\\.\\d+)?\\b"
        },
        {
          token: "support.function.flag.dockerfile",
          regex: "--[\\w-]+(=\\S+)?"
        },
        {
          token: "entity.name.filename.dockerfile",
          regex: "(\\.\\/|\\/)?[^\\s]+"
        }
      ]
    };
  };

  oop.inherits(DockerfileHighlightRules, TextHighlightRules);
  exports.DockerfileHighlightRules = DockerfileHighlightRules;
});
