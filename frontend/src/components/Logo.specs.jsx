import {describe, expect, test} from "vitest"
import {render, screen} from "@testing-library/react"
import Logo from "./Logo"



describe("Testing of the Logo component", () => {
    test("Logo is loaded properly on the page", () => {
        render(<Logo></Logo>)
        const logo = screen.getByLabelText("eventflow")
        expect(logo).toBeInTheDocument()
    })
})