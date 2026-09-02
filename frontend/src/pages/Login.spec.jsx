import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Login from "./Login";
import { AuthProvider } from "../auth";
import { MemoryRouter, Router } from "react-router";

describe("Testing of the Login page", () => {
    test("D5 Accessibilité issue", () => {
        //TestingLibraryElementError: Found a label with the text of: Email,
        // however no form control was found associated to that label.
        // Make sure you're using the "for" attribute or "aria-labelledby" attribute correctly.

        {
            /* <label>
                Email
              </label>
              <input
                class="input"
                required=""
                type="email"
                value="client@eventflow.test" */
        }

        render(
            <MemoryRouter>
                <AuthProvider>
                    <Login />
                </AuthProvider>
            </MemoryRouter>,
        );

        const input = screen.getAllByRole("textbox", {
            value: "client@eventflow.test",
        });
        const email = screen.getByLabelText("Email"); // ne peut pas recup
        expect(email).toBeInTheDocument();
        expect(input).toBeInTheDocument();
    });
});
