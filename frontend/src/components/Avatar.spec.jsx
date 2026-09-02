import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Avatar from "./Avatar";

describe("Testing of the Avatar component", () => {
    test("B4 Avatar shows first letters of the name", async () => {
        render(<Avatar user={{ full_name: "Camille Client" }}></Avatar>);
        const avat = await screen.findByText("CC");
        expect(avat).toBeInTheDocument();
    });

    test("B5 Logo is loaded properly on the page", async () => {
        render(<Avatar user={{ email: "client@eventflow.test" }}></Avatar>);
        const avar_fallback = await screen.findByText("C");
        expect(avar_fallback).toBeInTheDocument();
    });
});
