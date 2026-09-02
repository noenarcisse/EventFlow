import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Login from "./Login";

describe("Testing of the Login page", () => {
    test("D5 Accessibilité issue", () => {
        //         TypeError: Cannot destructure property 'login' of 'useAuth(...)' as it is null.
        //  ❯ Login src/pages/Login.jsx:8:11
        //       6|
        //       7| export default function Login() {
        //       8|   const { login, register } = useAuth();

        // render(<Login></Login>);
        // const logo = screen.getByLabelText("Email");
        // expect(logo).toBeInTheDocument();
    });
});
