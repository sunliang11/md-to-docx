-- Pandoc Lua filter: WeCom-friendly layout tweaks for DOCX output.

local COMPACT_TABLE_COLS = 6
local DEFAULT_IMAGE_WIDTH = "95%"

function CodeBlock(el)
  if not el.classes or #el.classes == 0 then
    el.attributes = el.attributes or {}
    el.attributes["custom-style"] = "Source Code"
  end
  return el
end

function BlockQuote(el)
  -- Wrap quote body so DOCX uses Block Text paragraph style consistently.
  return pandoc.Div(
    el.content,
    pandoc.Attr("", {}, { ["custom-style"] = "Block Text" })
  )
end

function HorizontalRule(el)
  return el
end

function Table(el)
  local ncol = 0
  if el.colspecs then
    ncol = #el.colspecs
  elseif el.bodies and #el.bodies > 0 and el.bodies[1].body then
    for _, row in ipairs(el.bodies[1].body) do
      if row.cells then
        ncol = math.max(ncol, #row.cells)
      end
    end
  end
  if ncol > COMPACT_TABLE_COLS then
    el.attributes = el.attributes or {}
    el.attributes["custom-style"] = "Compact Table"
  end
  return el
end

function Image(el)
  el.attributes = el.attributes or {}
  if not el.attributes.width and not el.attributes.height then
    el.attributes.width = DEFAULT_IMAGE_WIDTH
  end
  return el
end
