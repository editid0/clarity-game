export default async function GamePage({ params }) {
    const { game_id } = await params;
    return (
        <>
            <p>{game_id}</p>
        </>
    )
}