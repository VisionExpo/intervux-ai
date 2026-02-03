type Props = {
    isSpeacking: boolean;
};

export default function Avatar3D({ isSpeacking }: Props) {
    return (
        <div style={{ fontSize: "4rem" }}>
            {isSpeacking ? "😮" : "🤐"}
        </div>
    );
}