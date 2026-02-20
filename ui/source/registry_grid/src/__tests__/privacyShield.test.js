import { describe, expect, it, vi } from "vitest";

import { initPrivacyShield } from "../../../../static/phi_redactor/camera_local/privacyShield.js";

function createEmitter() {
  const listeners = new Map();
  return {
    addEventListener(type, cb) {
      if (!listeners.has(type)) listeners.set(type, new Set());
      listeners.get(type).add(cb);
    },
    removeEventListener(type, cb) {
      listeners.get(type)?.delete(cb);
    },
    dispatch(type, event = {}) {
      const set = listeners.get(type);
      if (!set) return;
      for (const cb of set) cb(event);
    },
  };
}

function createShieldElement() {
  const emitter = createEmitter();
  const classes = new Set();
  const attrs = new Map();

  return {
    ...emitter,
    classList: {
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      contains(name) { return classes.has(name); },
    },
    setAttribute(name, value) {
      attrs.set(name, String(value));
    },
    getAttribute(name) {
      return attrs.get(name);
    },
  };
}

describe("privacy shield", () => {
  it("activates on visibility hidden and requires tap to resume", () => {
    const doc = createEmitter();
    doc.hidden = false;
    doc.getElementById = () => null;

    const win = createEmitter();
    const shield = createShieldElement();
    const onBackground = vi.fn();
    const onResumeRequested = vi.fn();

    initPrivacyShield({
      document: doc,
      window: win,
      shieldEl: shield,
      onBackground,
      onResumeRequested,
    });

    doc.hidden = true;
    doc.dispatch("visibilitychange");
    expect(onBackground).toHaveBeenCalledTimes(1);
    expect(shield.classList.contains("active")).toBe(true);

    doc.hidden = false;
    doc.dispatch("visibilitychange");
    expect(shield.classList.contains("active")).toBe(true);

    shield.dispatch("click");
    expect(onResumeRequested).toHaveBeenCalledTimes(1);
    expect(shield.classList.contains("active")).toBe(false);
  });

  it("activates on pagehide", () => {
    const doc = createEmitter();
    doc.hidden = false;
    doc.getElementById = () => null;

    const win = createEmitter();
    const shield = createShieldElement();
    const onBackground = vi.fn();

    initPrivacyShield({
      document: doc,
      window: win,
      shieldEl: shield,
      onBackground,
      onResumeRequested: vi.fn(),
    });

    win.dispatch("pagehide");
    expect(onBackground).toHaveBeenCalledTimes(1);
    expect(shield.classList.contains("active")).toBe(true);
  });

  it("does not activate when shouldActivate returns false", () => {
    const doc = createEmitter();
    doc.hidden = true;
    doc.getElementById = () => null;

    const win = createEmitter();
    const shield = createShieldElement();
    const onBackground = vi.fn();

    initPrivacyShield({
      document: doc,
      window: win,
      shieldEl: shield,
      shouldActivate: () => false,
      onBackground,
      onResumeRequested: vi.fn(),
    });

    doc.dispatch("visibilitychange");
    win.dispatch("pagehide");
    win.dispatch("blur");

    expect(onBackground).toHaveBeenCalledTimes(0);
    expect(shield.classList.contains("active")).toBe(false);
  });
});
