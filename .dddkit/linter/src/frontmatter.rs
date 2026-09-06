//! Flat `key: value` frontmatter scanner.
//!
//! Deliberately a port of `_common.parse_frontmatter`'s behaviour, not an
//! upgrade to a real YAML parser. dddkit frontmatter is never nested, and
//! matching Python's leniency byte for byte keeps the Rust linter from
//! rejecting files the Python one accepted. Tightening this into a strict
//! parse is a separate, announced change (see plan/013 hazard 2).

use std::collections::HashMap;

pub fn parse(text: &str) -> HashMap<String, String> {
    let mut fields = HashMap::new();
    if !text.starts_with("---") {
        return fields;
    }
    // Mirrors Python's `text.find("\n---", 3)`.
    let end = match text[3..].find("\n---") {
        Some(i) => 3 + i,
        None => return fields,
    };

    for line in text[3..end].lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') || !line.contains(':') {
            continue;
        }
        let (key, value) = match line.split_once(':') {
            Some(kv) => kv,
            None => continue,
        };
        let key = key.trim().to_string();
        let mut value = value.trim().to_string();

        // Strip matching surrounding quotes, as Python does.
        if value.len() >= 2 {
            let bytes = value.as_bytes();
            let first = bytes[0];
            let last = bytes[value.len() - 1];
            let is_quote = |b: u8| b == b'\'' || b == b'"';
            if is_quote(first) && is_quote(last) {
                value = value[1..value.len() - 1].to_string();
            }
        }
        fields.insert(key, value);
    }
    fields
}

/// An unfilled template placeholder, e.g. `[GENERATED_UUID]` or
/// `[e.g. src/**/catalog/]`. The leading bracket is the sentinel the whole
/// framework uses for "this hasn't been filled in yet".
pub fn is_placeholder(value: &str) -> bool {
    value.starts_with('[')
}

/// Returns the value only if present and actually filled in.
pub fn resolved<'a>(fields: &'a HashMap<String, String>, key: &str) -> Option<&'a str> {
    match fields.get(key) {
        Some(v) if !v.is_empty() && !is_placeholder(v) => Some(v.as_str()),
        _ => None,
    }
}
